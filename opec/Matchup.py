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

class Matchup(object):

    def __init__(self, cell_position, spacetime_position, reference_record):
        """
       Constructs a matchup object.

       @param cell_position a list containing the cell indices.

       @param spacetime_position a list containing the position in space and time.

       @param reference_record a record containing the reference positions in space and time.
        """

        self.__cell_position = cell_position
        self.__spacetime_position = spacetime_position
        self.__reference_record = reference_record
        self.__values = {}

    def get_cell_position(self):
        return self.__cell_position

    def get_spacetime_position(self):
        return self.__spacetime_position

    def get_reference_record(self):
        return self.__reference_record

    def add_variable_value(self, name, value):
        self.__values[name] = value

    def get_variable_values(self):
        return self.__values

    cell_position = property(get_cell_position)
    spacetime_position = property(get_spacetime_position)
    reference_record = property(get_reference_record)
    values = property(get_variable_values)

    def __str__(self):
        return ', '.join('%s: %s' % (k.replace('_Matchup__', ''), vars(self)[k]) for k in vars(self))

