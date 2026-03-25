from .base import StoreBase
from .generic import GenericStoreMixin
from .strings import StringStoreMixin
from .lists import ListStoreMixin
from .hashes import HashStoreMixin
from .redis_set import SetStoreMixin
from .zsets import ZSetStoreMixin

class DataStore(
    ZSetStoreMixin,
    SetStoreMixin,
    HashStoreMixin,
    ListStoreMixin,
    StringStoreMixin,
    GenericStoreMixin,
    StoreBase,
):
    pass

db = DataStore()