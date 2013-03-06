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
    false_mask = np.zeros(len(values))
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