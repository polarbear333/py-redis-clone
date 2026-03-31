@dataclass
class PersistenceConfig:
    rdb_path: str = "dump.rdb"
    rdb_save_interval: float = 300.0
    aof_enabled: bool = False
    aof_path: str = "appendonly.aof"
    aof_fsync_policy: str = "everysec"

@dataclass
class ReplicationConfig:        
    role: str = "master"         # "master" | "slave"
    master_host: str | None = None
    master_port: int | None = None
    repl_id: str = ""            
    repl_offset: int = 0

@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 6379
    persistence: PersistenceConfig = field(default_factory=PersistenceConfig)
    replication: ReplicationConfig = field(default_factory=ReplicationConfig)