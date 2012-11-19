from __future__ import print_function
from src.main.python.InternalDataStorage import InternalDataStorage

class UserFriendlyInteractiveDataStorage(object):

    def __init__(self, *args, **kwargs):
        self.internalDataStorage = InternalDataStorage(*args, **kwargs)

    def list_model_vars(self):
        return self.internalDataStorage.get_model_vars()

    def close(self):
        self.internalDataStorage.close()

    def list_ref_vars(self):
        return self.internalDataStorage.get_ref_vars()
