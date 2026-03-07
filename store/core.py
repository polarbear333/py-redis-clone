from .base import StoreBase
from .generic import GenericStoreMixin
from .strings import StringStoreMixin

class DataStore(StringStoreMixin, GenericStoreMixin, StoreBase):
    pass

db = DataStore()