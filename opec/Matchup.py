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
from opec.Utils import retrieve_origin

class Matchup(object):

    def __init__(self, cell_position, spacetime_position, reference_record):
        self.__cell_position = cell_position
        self.__spacetime_position = spacetime_position
        self.__reference_record = reference_record

    def get_cell_position(self):
        return self.__cell_position

    def get_spacetime_position(self):
        return self.__spacetime_position

    def get_reference_record(self):
        return self.__reference_record

    def get_ref_value(self, variable_name, data):
        reference_dimensions = data.get_reference_dimensions(variable_name)
        if len(reference_dimensions) == 1:
            return data.read_reference(variable_name, [self.__reference_record.record_number])
        else:
            cell_position_copy = self.cell_position[:]
            if self.__reference_record.time is None:
                cell_position_copy[0] = None
            if self.__reference_record.depth is None:
                cell_position_copy[1] = None
            origin = list(retrieve_origin(cell_position_copy))
            return data.read_reference(variable_name, origin)

    def get_model_value(self, variable_name, data):
        origin = list(retrieve_origin(self.cell_position))
        return data.read_model(variable_name, origin)

    cell_position = property(get_cell_position)
    spacetime_position = property(get_spacetime_position)
    reference_record = property(get_reference_record)

    def __str__(self):
        return ', '.join('%s: %s' % (k.replace('_Matchup__', ''), vars(self)[k]) for k in vars(self))

