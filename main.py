import asyncio
import argparse
import logging
from config import PersistenceConfig
from startup import boot
from server import start_server
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def parse_config() -> PersistenceConfig:
    parser = argparse.ArgumentParser(description="Redis Clone")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6379)
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
    return PersistenceConfig(
        rdb_path=args.rdb_path,
        rdb_save_interval=args.rdb_save_interval,
        aof_enabled=args.aof_enabled,
        aof_path=args.aof_path,
        aof_fsync_policy=args.aof_fsync_policy,
    ), args.host, args.port

async def main() -> None:
    config, host, port = parse_config()
    app_ctx = await boot(config)
    await start_server(app_ctx, host=host, port=port)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server shutting down gracefully.")