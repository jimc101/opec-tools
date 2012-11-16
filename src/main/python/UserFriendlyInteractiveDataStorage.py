from __future__ import print_function
from sys import stdout
from src.main.python.InternalDataStorage import InternalDataStorage

class UserFriendlyInteractiveDataStorage(object):

    def __init__(self, *args, **kwargs):
        self.internalDataStorage = InternalDataStorage(*args, **kwargs)

    def list_model_vars(self, printStream=stdout):
        model_vars = self.internalDataStorage.get_model_vars()
        printStream.write(model_vars)

    def close(self):
        self.internalDataStorage.close()

    def list_ref_vars(self, printStream=stdout):
        ref_vars = self.internalDataStorage.get_model_vars()
        printStream.write(ref_vars)
