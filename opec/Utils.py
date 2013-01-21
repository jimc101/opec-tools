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

def get_logging_formatter():
    return MyFormatter(format='[%(levelname)s] %(asctime)-15s - %(message)s', datefmt='%Y-%d-%mT%H:%M:%S')

def retrieve_origin(cell_positions):
    for p in cell_positions:
        if p is not None:
            yield p