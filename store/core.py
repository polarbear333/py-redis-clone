from .base import StoreBase
from .generic import GenericStoreMixin
from .strings import StringStoreMixin
from .lists import ListStoreMixin
from .hashes import HashStoreMixin
from .redis_set import SetStoreMixin
from .zsets import ZSetStoreMixin
from .persistence_mixin import PersistenceMixin

class DataStore(
    ZSetStoreMixin,
    SetStoreMixin,
    HashStoreMixin,
    ListStoreMixin,
    StringStoreMixin,
    GenericStoreMixin,
    PersistenceMixin,
    StoreBase,
):
    def __init__(self, config=None):
        super().__init__()
        self.config = config