__author__ = 'Thomas Storm'

import logging

class MyFormatter(logging.Formatter):

    def __init__(self, **kwargs):
        super(MyFormatter, self).__init__(fmt=kwargs['format'], datefmt=kwargs['datefmt'])

    def format(self, record):
        str = super(MyFormatter, self).format(record)
        return str.replace('DEBUG', 'D')\
        .replace('INFO', 'I')\
        .replace('WARNING', 'W')\
        .replace('ERROR', 'E')\
        .replace('CRITICAL', 'C')\
        .replace('FATAL', 'C')

handler = logging.StreamHandler()
formatter = MyFormatter(format='[%(levelname)s] %(asctime)-15s - %(message)s', datefmt='%Y-%d-%mT%H:%M:%S')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)
