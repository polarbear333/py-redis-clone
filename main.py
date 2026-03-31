import asyncio
import argparse
import logging
from config import PersistenceConfig
from store import DataStore
from persistence.aof import AOFWriter, replay
from server import start_server, dispatch
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def rdb_save_loop(store: DataStore, interval: float) -> None:
    if interval <= 0:
        return
    loop = asyncio.get_running_loop()
    while True:
        await asyncio.sleep(interval)
        logging.info("Starting background RDB save...")
        await loop.run_in_executor(None, store.save_rdb)
        logging.info("RDB save completed.")

async def main() -> None:
    parser = argparse.ArgumentParser(description="Redis Clone")
    parser.add_argument("--rdb-path", default="dump.rdb")
    parser.add_argument("--rdb-save-interval", type=float, default=300.0)
    parser.add_argument("--aof-enabled", action="store_true")
    parser.add_argument("--aof-path", default="appendonly.aof")
    parser.add_argument(
        "--aof-fsync-policy",
        choices=["always", "everysec", "no"],
        default="everysec",
    )
    args = parser.parse_args()

    config = PersistenceConfig(
        rdb_path=args.rdb_path,
        rdb_save_interval=args.rdb_save_interval,
        aof_enabled=args.aof_enabled,
        aof_path=args.aof_path,
        aof_fsync_policy=args.aof_fsync_policy,
    )
    store = DataStore(config)
    logging.info(f"Loading RDB from {config.rdb_path}...")
    store.load_rdb()
    aof_writer = None
    if config.aof_enabled:
        logging.info(f"Replaying AOF from {config.aof_path}...")

        async def dispatch_wrapper(cmd_list, aof_writer=None):
            return await dispatch(cmd_list, store, aof_writer=None)

        ops = await replay(config.aof_path, dispatch_wrapper)
        logging.info(f"Replayed {ops} operations from AOF.")
        aof_writer = AOFWriter(config.aof_path, config.aof_fsync_policy)
        asyncio.create_task(aof_writer.fsync_loop())

    asyncio.create_task(rdb_save_loop(store, config.rdb_save_interval))
    await start_server(store=store, aof_writer=aof_writer)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server shutting down gracefully.")