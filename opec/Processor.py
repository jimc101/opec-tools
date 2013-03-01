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

import numpy as np
import numpy.ma as ma
import scipy.stats.mstats as mstats
from opec.Configuration import get_default_config

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

def mean(values):
    return np.mean(values)

def stddev(values, ddof):
    return ma.std(values, ddof=ddof)

def percentiles(values, alphap, betap):
    return mstats.mquantiles(values, [0.5, 0.9, 0.95], alphap, betap)

def minmax(values):
    return [ma.min(values), ma.max(values)]

def rmse(reference_values, values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    squared_errors = (values - reference_values) ** 2
    return ma.sqrt(ma.mean(squared_errors))

def normalised_rmse(reference_values, values, ddof, correlation):
    """
    according to "Diagrams for coupled hydrodynamic-ecosystem model skill assessment", Joliff et. al. 2009
    """
    normalised_stddev = ma.std(values, ddof=ddof) / ma.std(reference_values, ddof=ddof)
    return ma.sqrt(1 + normalised_stddev**2 - 2 * normalised_stddev * correlation)

def bias(reference_values, values):
    """
    according to http://en.wikipedia.org/wiki/Bias_of_an_estimator
    """
    return ma.mean(reference_values) - ma.mean(values)

def unbiased_rmse(reference_values, values):
    squared_differences = ((values - ma.mean(values)) - (reference_values - ma.mean(reference_values))) ** 2
    squared_differences /= ma.count(values)
    return ma.sqrt(ma.sum(squared_differences))

def correlation(reference_values, values):
    if len(ma.unique(reference_values)) == 1 or len(ma.unique(values)) == 1:
        return np.nan # if all reference or model values are equal, no sensible correlation coefficient can be computed.
    return ma.corrcoef(values, reference_values)[0, 1]

def percentage_model_bias(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    return ma.sum(reference_values - model_values) * 100 / ma.sum(reference_values)


def reliability_index(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    n = 1 / ma.count(reference_values)
    return ma.exp(ma.sqrt(n * ma.sum(ma.power(ma.log10(reference_values / model_values), 2))))

def model_efficiency(reference_values, model_values):
    """
    Nash-Sutcliffe model efficiency according to MEECE D2.7 User guide and report outlining validation methodology
    """
    if len(ma.unique(reference_values)) == 1:
        return np.nan # if all reference values are equal, no sensible model efficiency can be computed.
    return 1 - ma.sum(ma.power(reference_values - model_values, 2)) / ma.sum(ma.power(reference_values - np.mean(reference_values), 2))

def create_masked_array(values):
    false_mask = np.zeros(len(values))
    if type(values) is not ma.core.MaskedArray:
        values = ma.array(values, mask=false_mask)
    return values

def harmonise(reference_values, model_values):
    reference_values = create_masked_array(reference_values)
    model_values = create_masked_array(model_values)
    reference_values.mask = reference_values.mask | model_values.mask
    model_values.mask = reference_values.mask | model_values.mask
    return reference_values, model_values

def calculate_statistics(matchups=None, data=None, model_name=None, ref_name=None, reference_values_aligned=None, model_values_aligned=None, reference_values_original=None, model_values_original=None, unit=None, config=None):
    """Calculate the statistics for either the given matchups or the given reference and model arrays.
    If matchups are given, the reference and model arrays are NOT considered and vice versa.
    If matchups are given, the data, model_name, and ref_name arguments are mandatory. Otherwise, it is recommended to
    provide model_name and ref_name in order to create meaningful output.

    Note that there might be gridded reference variables that have dimensionality different to those of the model variable.
    In such cases, the data with the lesser dimensionality is duplicated and thus brought onto the same grid as the other data.
    So, for example, if the model variable has the dimensions time, lat, and lon, while the reference variable has only lat and lon,
    there are practically matchups created for each point in time of the model variable.
    Since using such a blown-up variable might yield slightly different results for the percentiles,
    their original values can and should be passed into this method as well, as reference_values_original and
    as model_values_original.
    """

    if matchups is not None:
        if model_name is None or ref_name is None or data is None:
            raise ValueError('Cannot calculate statistics from matchups: data, model_name, or ref_name missing.')
        reference_values_aligned, model_values_aligned = extract_values(matchups, data, ref_name, model_name)
    elif reference_values_aligned is None or model_values_aligned is None:
        raise ValueError('Cannot calculate statistics from matchups: missing either matchups or reference and model values.')

    reference_values_aligned, model_values_aligned = harmonise(reference_values_aligned.flatten(), model_values_aligned.flatten())
    if ma.count(model_values_aligned) != ma.count(reference_values_aligned):
        raise ValueError("len(values) != len(reference_values_aligned)")

    if reference_values_original is None:
        reference_values_original = reference_values_aligned
    if model_values_original is None:
        model_values_original = model_values_aligned

    if config is None:
        config = get_default_config()

    model_percentiles = percentiles(model_values_original.flatten(), config.alpha, config.beta)
    ref_percentiles = percentiles(reference_values_original, config.alpha, config.beta)
    model_minmax = minmax(model_values_original)
    ref_minmax = minmax(reference_values_original)
    stats = dict()
    stats['model_name'] = model_name
    stats['ref_name'] = ref_name
    stats['unit'] = unit
    stats['rmse'] = rmse(reference_values_aligned, model_values_aligned)
    stats['corrcoeff'] = correlation(reference_values_aligned, model_values_aligned)
    stats['unbiased_rmse'] = unbiased_rmse(reference_values_aligned, model_values_aligned)
    stats['normalised_rmse'] = normalised_rmse(reference_values_aligned, model_values_aligned, config.ddof, stats['corrcoeff'])
    stats['pbias'] = percentage_model_bias(reference_values_aligned, model_values_aligned)
    stats['bias'] = bias(reference_values_aligned, model_values_aligned)
    stats['reliability_index'] = reliability_index(reference_values_aligned, model_values_aligned)
    stats['model_efficiency'] = model_efficiency(reference_values_aligned, model_values_aligned)
    stats['mean'] = mean(model_values_original)
    stats['ref_mean'] = mean(reference_values_original)
    stats['stddev'] = stddev(model_values_original, config.ddof)
    stats['ref_stddev'] = stddev(reference_values_original, config.ddof)
    stats['median'] = model_percentiles[0]
    stats['ref_median'] = ref_percentiles[0]
    stats['p90'] = model_percentiles[1]
    stats['ref_p90'] = ref_percentiles[1]
    stats['p95'] = model_percentiles[2]
    stats['ref_p95'] = ref_percentiles[2]
    stats['min'] = model_minmax[0]
    stats['ref_min'] = ref_minmax[0]
    stats['max'] = model_minmax[1]
    stats['ref_max'] = ref_minmax[1]
    return stats