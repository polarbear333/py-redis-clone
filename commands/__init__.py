from typing import Callable, Dict, Awaitable, List

CommandHandler = Callable[[List[bytes]], Awaitable[bytes]]
REGISTRY: Dict[bytes, CommandHandler] = {}

def command(name: str) -> Callable[[CommandHandler], CommandHandler]:
    def decorator(func: CommandHandler) -> CommandHandler:
        key = name.upper().encode('utf-8')
        REGISTRY[key] = func
        return func
    return decorator