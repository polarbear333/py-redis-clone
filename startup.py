import asyncio
import logging
from typing import Optional
from config import PersistenceConfig
from store import DataStore
from app_context import AppContext
from persistence.aof import AOFWriter, replay
from persistence import rdb
from middleware.aof import AOFMiddleware
from server import dispatch_core

logger = logging.getLogger(__name__)

async def _rdb_save_loop(store: DataStore, interval: float) -> None:
    if interval <= 0:
        return
    loop = asyncio.get_running_loop()
    while True:
        await asyncio.sleep(interval)
        logger.info("Starting background RDB save...")
        await loop.run_in_executor(None, store.save_rdb)
        logger.info("RDB save completed.")

async def boot(config: PersistenceConfig) -> AppContext:
    store = DataStore(config)
    logger.info(f"Loading RDB from {config.rdb_path}...")
    store.load_rdb()

    aof_writer: Optional[AOFWriter] = None
    fsync_task = None
    if config.aof_enabled:
        logger.info(f"Replaying AOF from {config.aof_path}...")
        async def dispatch_wrapper(cmd_list: list) -> bytes:
            return await dispatch_core(cmd_list, store)
        ops = await replay(config.aof_path, dispatch_wrapper)
        logger.info(f"Replayed {ops} operations from AOF.")
        aof_writer = AOFWriter(config.aof_path, config.aof_fsync_policy)
        fsync_task = asyncio.create_task(aof_writer.fsync_loop())

    ctx = AppContext(store=store, config=config, aof_writer=aof_writer)
    store._watch_registry = ctx.watch_registry

    if fsync_task:
        ctx.bg_tasks.append(fsync_task)
    if aof_writer:
        ctx.middleware.append(AOFMiddleware(aof_writer))
    if config.rdb_save_interval > 0:
        ctx.bg_tasks.append(
            asyncio.create_task(_rdb_save_loop(store, config.rdb_save_interval))
        )
    return ctx