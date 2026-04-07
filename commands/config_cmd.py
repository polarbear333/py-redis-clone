from __future__ import annotations
import fnmatch
from handler import serialize, RESPError
from . import command, Context

_CONFIG_PARAMS = {
    b"save": (
        lambda cfg: str(int(cfg.rdb_save_interval)).encode(),
        lambda cfg, v: setattr(cfg, "rdb_save_interval", float(v)),
    ),
    b"appendonly": (
        lambda cfg: b"yes" if cfg.aof_enabled else b"no",
        lambda cfg, v: setattr(cfg, "aof_enabled", v.lower() == b"yes"),
    ),
    b"appendfsync": (
        lambda cfg: cfg.aof_fsync_policy.encode(),
        lambda cfg, v: setattr(cfg, "aof_fsync_policy", v.decode()),
    ),
    b"dbfilename": (
        lambda cfg: cfg.rdb_path.encode(),
        lambda cfg, v: setattr(cfg, "rdb_path", v.decode()),
    ),
    b"appendfilename": (
        lambda cfg: cfg.aof_path.encode(),
        lambda cfg, v: setattr(cfg, "aof_path", v.decode()),
    ),
}

def _get_config(app_ctx) -> object:
    """Return the PersistenceConfig stored on AppContext."""
    return app_ctx.config

@command("CONFIG")
async def cmd_config(ctx: Context, args: list) -> bytes:
    if not args:
        return serialize(
            RESPError("ERR wrong number of arguments for 'CONFIG' command")
        )
    sub = args[0].upper()

    if sub == b"GET":
        if len(args) < 2:
            return serialize(RESPError("ERR wrong number of arguments for 'CONFIG|GET' command"))
        if ctx.app_ctx is None:
            return serialize([])
        pattern = args[1].lower()
        cfg = _get_config(ctx.app_ctx)
        result = []
        for param_key, (getter, _) in _CONFIG_PARAMS.items():
            if fnmatch.fnmatchcase(param_key, pattern):
                result.append(param_key)
                result.append(getter(cfg))
        return serialize(result)

    if sub == b"SET":
        if len(args) < 3 or len(args) % 2 == 0:
            return serialize(
                RESPError("ERR wrong number of arguments for 'CONFIG|SET' command")
            )
        if ctx.app_ctx is None:
            return serialize(RESPError("ERR no app context"))
        cfg = _get_config(ctx.app_ctx)
        pairs = list(zip(args[1::2], args[2::2]))
        for param, value in pairs:
            entry = _CONFIG_PARAMS.get(param.lower())
            if entry is None:
                return serialize(
                    RESPError(f"ERR unknown option or number of arguments for CONFIG SET - '{param.decode()}'")
                )
            _, setter = entry
            try:
                setter(cfg, value)
            except (ValueError, TypeError) as exc:
                return serialize(RESPError(f"ERR {exc}"))
        return serialize(b"OK")

    if sub == b"REWRITE":
        # stub 
        return serialize(b"OK")

    if sub == b"RESETSTAT":
        if ctx.app_ctx is not None:
            ctx.app_ctx.stats.commands_processed = 0
        return serialize(b"OK")

    return serialize(
        RESPError(f"ERR unknown subcommand '{sub.decode()}'. Try CONFIG HELP.")
    )