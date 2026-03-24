import asyncio
import logging, socket
from handler import RESPReader, serialize, RESPError
from store import DataStore, db 
from commands import REGISTRY, Context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    logging.info(f"client connected: {addr}")
    resp_reader = RESPReader(reader)
    try:
        while True:
            try:
                command_list = await resp_reader.read_command()
            except OSError:
                break
            except RESPError as e:
                writer.write(serialize(e))
                try:
                    await writer.drain()
                except (ConnectionResetError, BrokenPipeError):
                    pass
                break
            try:
                reply = await dispatch(command_list, db)
            except Exception as e:
                logging.error(f"dispatch error for {addr}: {e}")
                reply = serialize(RESPError("ERR internal server error"))
            ## immediate write
            writer.write(reply)
            try:
                await writer.drain()
            except (ConnectionResetError, BrokenPipeError):
                break

    except Exception as e:
        logging.error(f"unexpected error handling client {addr}: {e}")
    finally:
        logging.info(f"client disconnected: {addr}")
        writer.close()
        await writer.wait_closed()

async def dispatch(command_list: list[bytes], store: DataStore) -> bytes:
    ## look up and invoke the handler for a RESP command
    cmd_name: bytes = command_list[0].upper()
    cmd_text = cmd_name.decode() 
    args = command_list[1:]
    handler = REGISTRY.get(cmd_name)

    if not handler:
        return serialize(RESPError(f"unknown command '{cmd_text}'"))
    ## context get consutrct per request
    ctx = Context(store)
    try:
        return await handler(ctx, args)
    except RESPError as e:
        return serialize(e)
    except Exception as e:
        logging.error(f"command error in {cmd_text}: {e}")
        return serialize(RESPError("internal server error"))
        
async def start_server(host: str = '127.0.0.1', port: int = 6379):
    server = await asyncio.start_server(handle_client, host, port)
    addrs = ', '.join(str(sockets.getsockname()) for sockets in server.sockets)
    logging.info(f"serving Redis clone on {addrs}")
    async with server:
        await server.serve_forever()