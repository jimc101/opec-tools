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
        return None, None
    if dim_count_1 < dim_count_2:
        array_to_reduce = array_2
        dim_difference = dim_count_2 - dim_count_1
    else:
        array_to_reduce = array_1
        dim_difference = dim_count_1 - dim_count_2

    array_list = []
    for j in range(dim_difference):
        array_list.append(np.arange(array_to_reduce.shape[j]))
    cartesian_product = cartesian(array_list)
    result_list = [tuple(a) for a in cartesian_product]

    if dim_count_1 > dim_count_2:
        return result_list, None
    if dim_count_1 < dim_count_2:
        return None, result_list




def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in range(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out