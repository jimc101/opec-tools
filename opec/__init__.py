# Copyright (C) 2013 Brockmann Consult GmbH (info@brockmann-consult.de)
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see http://www.gnu.org/licenses/gpl.html

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

handler = logging.StreamHandler()
handler.setFormatter(get_logging_formatter())
logging.getLogger().addHandler(handler)