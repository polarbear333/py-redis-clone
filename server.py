# server.py
import asyncio
import logging
from handler import RESPReader, serialize, RESPError
from commands import REGISTRY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    logging.info(f"client connected: {addr}")
    resp_reader = RESPReader(reader)
    try:
        while True:
            try:
                command_list = await resp_reader.read_command()
            except ConnectionError:
                break 
            except ConnectionAbortedError:
                break 
            if not command_list:
                continue
            cmd_name_bytes = command_list[0].upper()
            args = command_list[1:]
            handler = REGISTRY.get(cmd_name_bytes)

            if handler:
                try:
                    response_bytes = await handler(args)
                except Exception as e:
                    logging.error(f"Command error: {e}")
                    response_bytes = serialize(RESPError("Internal server error"))
            else:
                response_bytes = serialize(RESPError(f"unknown command '{cmd_name_bytes.decode()}'"))
            writer.write(response_bytes)
            await writer.drain()

    except Exception as e:
        logging.error(f"unexpected error handling client {addr}: {e}")
    finally:
        logging.info(f"client disconnected: {addr}")
        writer.close()
        await writer.wait_closed()

async def start_server(host: str = '127.0.0.1', port: int = 6379):
    server = await asyncio.start_server(handle_client, host, port)
    addrs = ', '.join(str(sockets.getsockname()) for sockets in server.sockets)
    logging.info(f"serving Redis clone on {addrs}")

    async with server:
        await server.serve_forever()