from .base import StoreBase
from .generic import GenericStoreMixin
from .strings import StringStoreMixin
from .lists import ListStoreMixin

class DataStore(StringStoreMixin, GenericStoreMixin, StoreBase, ListStoreMixin):
    pass

db = DataStore()