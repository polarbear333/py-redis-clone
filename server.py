import asyncio
import logging
from typing import List, Optional
from handler import RESPReader, serialize, RESPError
from store import DataStore
from commands import REGISTRY, Context
from middleware.base import DispatchFn
from middleware.transaction import TransactionMiddleware
from app_context import AppContext
from transaction import ClientState

logger = logging.getLogger(__name__)

async def dispatch_core(
        command_list: List[bytes],
        store: DataStore,
        tx_state: Optional[ClientState] = None,
        watch_registry=None,
        dispatch_fn: Optional[DispatchFn] = None,
    ) -> bytes:
    cmd_name = command_list[0].upper()
    handler = REGISTRY.get(cmd_name)
    if not handler:
        return serialize(RESPError(f"unknown command '{cmd_name.decode()}'"))

    ctx = Context(
        db=store,
        tx_state=tx_state,
        watch_registry=watch_registry,
        dispatch=dispatch_fn,
    )
    try:
        return await handler(ctx, command_list[1:])
    except RESPError as e:
        return serialize(e)
    except Exception as e:
        logger.error(f"command error in {cmd_name.decode()}: {e}")
        return serialize(RESPError("ERR internal server error"))

def _build_pipeline(app_ctx: AppContext):
    """
    given a ClientState, produces a DispatchFn
    for that connection.

    Middleware order (outermost -> innermost):
      TransactionMiddleware -- queues commands during MULTI
      AOFMiddleware -- logs writes to append-only file
      dispatch_core -- executes the command
    """
    def make_pipeline(tx_state: ClientState) -> DispatchFn:
        async def core(command_list: List[bytes]) -> bytes:
            return await dispatch_core(
                command_list,
                app_ctx.store,
                tx_state=tx_state,
                watch_registry=app_ctx.watch_registry,
                dispatch_fn=core,
            )

        pipeline: DispatchFn = core
        for mw in reversed(app_ctx.middleware):
            def make_next(middleware, inner):
                async def next_fn(command_list):
                    return await middleware(command_list, inner)
                return next_fn
            pipeline = make_next(mw, pipeline)

        tx_mw = TransactionMiddleware(tx_state, app_ctx.watch_registry)
        outer = pipeline
        async def tx_layer(command_list: List[bytes]) -> bytes:
            return await tx_mw(command_list, outer)
        return tx_layer
    
    return make_pipeline

async def handle_client(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        make_pipeline,
    ) -> None:
    addr = writer.get_extra_info('peername')
    logger.info(f"client connected: {addr}")

    tx_state = ClientState()
    pipeline = make_pipeline(tx_state)
    resp_reader = RESPReader(reader)

    try:
        while True:
            try:
                command_list = await resp_reader.read_command()
            except ConnectionAbortedError:
                break
            except OSError:
                break
            except RESPError as e:
                if tx_state.in_multi:
                    tx_state.has_error = True
                writer.write(serialize(e))
                try:
                    await writer.drain()
                except (ConnectionResetError, BrokenPipeError):
                    pass
                break

            try:
                reply = await pipeline(command_list)
            except Exception as e:
                logger.error(f"unhandled pipeline error for {addr}: {e}")
                reply = serialize(RESPError("ERR internal server error"))

            writer.write(reply)
            try:
                await writer.drain()
            except (ConnectionResetError, BrokenPipeError):
                break
    finally:
        logger.info(f"client disconnected: {addr}")
        writer.close()
        await writer.wait_closed()

async def _active_expiry_loop(store: DataStore, interval: float = 0.1) -> None:
    while True:
        await asyncio.sleep(interval)
        store._probabilistic_expire()

async def start_server(app_ctx: AppContext, host: str = "127.0.0.1", port: int = 6379) -> None:
    make_pipeline = _build_pipeline(app_ctx)

    async def client_cb(reader, writer):
        await handle_client(reader, writer, make_pipeline)

    expiry_task = asyncio.create_task(_active_expiry_loop(app_ctx.store))
    server = await asyncio.start_server(client_cb, host, port)
    addrs = ", ".join(str(s.getsockname()) for s in server.sockets)
    logger.info(f"serving Redis clone on {addrs}")
    try:
        async with server:
            await server.serve_forever()
    finally:
        all_tasks = [expiry_task] + app_ctx.bg_tasks
        for task in all_tasks:
            task.cancel()
        await asyncio.gather(*all_tasks, return_exceptions=True)
        if app_ctx.aof_writer:
            app_ctx.aof_writer.close()