# main.py
import asyncio
import logging
import commands.strings 

from server import start_server

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logging.info("Server shutting down gracefully.")