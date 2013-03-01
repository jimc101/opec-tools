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

import numpy as np

def retrieve_origin(cell_positions):
    for p in cell_positions:
        if p is not None:
            yield p


def align(array_1, array_2):
    dim_count_1 = len(array_1.shape)
    dim_count_2 = len(array_2.shape)
    if dim_count_1 == dim_count_2:
        return array_1, array_2
    if dim_count_1 > dim_count_2:
        array_to_extend = array_2
        extension_array = array_2
        constant_array = array_1
        dim_difference = dim_count_1 - dim_count_2
    else:
        array_to_extend = array_1
        extension_array = array_1
        constant_array = array_2
        dim_difference = dim_count_2 - dim_count_1

    index = dim_difference
    for d in range(len(array_to_extend.shape)):
        if not constant_array.shape[index] == array_to_extend.shape[d]:
            raise ValueError('Arrays are not alignable.')
        index += 1

    p = 1
    for d in range(dim_difference):
        p *= constant_array.shape[d]

    for i in range(p - 1):
        array_to_extend = np.ma.concatenate((array_to_extend, extension_array))

    if dim_count_1 > dim_count_2:
        return array_1, array_to_extend.reshape(array_1.shape)
    if dim_count_1 < dim_count_2:
        return array_to_extend.reshape(array_2.shape), array_2