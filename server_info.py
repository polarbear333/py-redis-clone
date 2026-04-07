from __future__ import annotations
import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app_context import AppContext

_VERSION = "0.1.0"
_MODE = "standalone"
_OS = sys.platform
_ARCH = "64"
_REDIS_GIT_SHA1 = "00000000"

def _uptime_seconds(start_time: float) -> int:
    return int(time.time() - start_time)

def _section_server(app_ctx: "AppContext") -> str:
    up = _uptime_seconds(app_ctx.stats.start_time)
    lines = [
        "# Server",
        f"redis_version:{_VERSION}",
        f"redis_git_sha1:{_REDIS_GIT_SHA1}",
        f"redis_git_dirty:0",
        f"redis_build_id:0",
        f"redis_mode:{_MODE}",
        f"os:{_OS}",
        f"arch_bits:{_ARCH}",
        f"tcp_port:{getattr(app_ctx.config, 'port', 6379)}",
        f"uptime_in_seconds:{up}",
        f"uptime_in_days:{up // 86400}",
        f"hz:10",
        f"configured_hz:10",
        f"aof_rewrite_incremental_fsync:yes",
        f"rdb_save_incremental_fsync:yes",
    ]
    return "\r\n".join(lines)

def _section_clients(app_ctx: "AppContext") -> str:
    lines = [
        "# Clients",
        f"connected_clients:{app_ctx.stats.connected_clients}",
        "blocked_clients:0",
        "tracking_clients:0",
    ]
    return "\r\n".join(lines)

def _section_memory(app_ctx: "AppContext") -> str:
    used = sys.getsizeof(app_ctx.store._data)
    lines = [
        "# Memory",
        f"used_memory:{used}",
        f"used_memory_human:{used // 1024}K",
        f"used_memory_rss:{used}",
        f"mem_fragmentation_ratio:1.0",
        f"mem_allocator:libc",
    ]
    return "\r\n".join(lines)

def _section_stats(app_ctx: "AppContext") -> str:
    lines = [
        "# Stats",
        f"total_connections_received:{app_ctx.stats.total_connections_received}",
        f"total_commands_processed:{app_ctx.stats.commands_processed}",
        "instantaneous_ops_per_sec:0",
        "rejected_connections:0",
        "expired_keys:0",
        "evicted_keys:0",
        "keyspace_hits:0",
        "keyspace_misses:0",
    ]
    return "\r\n".join(lines)

def _section_replication(app_ctx: "AppContext") -> str:
    from config import ReplicationConfig
    repl: ReplicationConfig = getattr(app_ctx.config, "replication", None)
    role = repl.role if repl else "master"
    repl_id = repl.repl_id if repl else "0" * 40
    offset = repl.repl_offset if repl else 0
    lines = [
        "# Replication",
        f"role:{role}",
        "connected_slaves:0",
        f"master_replid:{repl_id or '0' * 40}",
        f"master_repl_offset:{offset}",
        "repl_backlog_active:0",
        "repl_backlog_size:1048576",
        "repl_backlog_first_byte_offset:0",
        "repl_backlog_histlen:0",
    ]
    return "\r\n".join(lines)

def _section_keyspace(app_ctx: "AppContext") -> str:
    store = app_ctx.store
    total = len(store._data)
    lines = ["# Keyspace"]
    if total:
        lines.append(f"db0:keys={total},expires={len(store._expiry)},avg_ttl=0")
    return "\r\n".join(lines)

_SECTION_BUILDERS = {
    "server": _section_server,
    "clients": _section_clients,
    "memory": _section_memory,
    "stats": _section_stats,
    "replication": _section_replication,
    "keyspace": _section_keyspace,
}

_ALL_SECTIONS = list(_SECTION_BUILDERS.keys())

def build_info(section: str, app_ctx: "AppContext") -> str:
    """
    Return the INFO output for the requested section.
    Pass section="all" or "everything" (or omit by passing "") to get all sections.
    """
    section = section.lower()
    if section in ("", "all", "everything", "default"):
        parts = [_SECTION_BUILDERS[s](app_ctx) for s in _ALL_SECTIONS]
        return "\r\n\r\n".join(parts)
    builder = _SECTION_BUILDERS.get(section)
    if builder is None:
        return ""
    return builder(app_ctx)