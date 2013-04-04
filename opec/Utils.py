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
import numpy.ma as ma
import logging

def retrieve_origin(cell_positions):
    for p in cell_positions:
        if p is not None:
            yield p


def harmonise(reference_values, model_values):
    reference_values = create_masked_array(reference_values)
    model_values = create_masked_array(model_values)
    reference_values.mask = reference_values.mask | model_values.mask
    model_values.mask = reference_values.mask | model_values.mask
    return reference_values, model_values


def create_masked_array(values):
    false_mask = np.zeros(values.shape)
    if type(values) is not ma.core.MaskedArray:
        values = ma.array(values, mask=false_mask)
    return values


def extract_values(matchups, data, ref_name, model_name):
    logging.debug('Extracting values of variables \'%s\' and \'%s\'' % (ref_name, model_name))
    reference_values = np.ma.empty(len(matchups))
    model_values = np.ma.empty(len(matchups))
    index = 0
    for matchup in matchups:
        reference_values[index] = matchup.get_ref_value(ref_name, data)
        model_values[index] = matchup.get_model_value(model_name, data)
        index += 1
    return reference_values, model_values

def get_unit(ncfile, variable_name):
    if ncfile.get_variable(variable_name):
        return ncfile.get_variable_attribute(variable_name, 'units')
    return None


def create_test_file():
    '''
    Creates a test file. Don't use.
    '''
    import numpy.random as random
    import numpy as np
    from netCDF4 import Dataset
    d = Dataset('c:/temp/input/big_gridded_big_ref.nc', 'a', format='NETCDF4_CLASSIC')
    d.variables['time'][:] = np.arange(1261440000, 1261465000, 50)
    d.variables['depth'][:] = np.arange(0.001, 0.005, 0.001)
    d.variables['lat'][:] = np.linspace(-90, 90, 200)
    d.variables['lon'][:] = np.linspace(-180, 180, 400)
    d.variables['time_ref'][:] = np.arange(1261440000, 1261940000, 100)
    d.variables['depth_ref'][:] = random.rand(5000)
    d.variables['lat_ref'][:] = random.rand(5000) * 180 - 90
    d.variables['lon_ref'][:] = random.rand(5000) * 360 - 180
    d.variables['chl_ref'][:] = random.rand(5000)
    d.variables['chl'][:] = random.rand(500, 4, 200, 400)
    d.variables['sst'][:] = random.rand(500, 4, 200, 400) + 1
    d.variables['sst_ref'][:] = random.rand(500, 4, 200, 400) * 0.5 + 1
    d.close()


def ensure_list(var=None):
    if var is not None and not type(var) == list:
        var = [var]
    return var
