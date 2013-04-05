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
import scipy.stats.mstats as mstats
from opec.configuration import get_default_config


def mean(values):
    return np.mean(values)


def stddev(values, ddof):
    return np.std(values, ddof=ddof)


def percentiles(values, alphap, betap):
    return mstats.mquantiles(values, [0.5, 0.9, 0.95], alphap, betap)


def minmax(values):
    return [np.min(values), np.max(values)]


def rmse(reference_values, values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    squared_errors = (values - reference_values) ** 2
    return np.sqrt(np.mean(squared_errors))


def normalised_rmse(reference_values, values, ddof, correlation):
    """
    according to "Diagrams for coupled hydrodynamic-ecosystem model skill assessment", Joliff et. al. 2009
    """
    normalised_stddev = np.std(values, ddof=ddof) / np.std(reference_values, ddof=ddof)
    return np.sqrt(1 + normalised_stddev**2 - 2 * normalised_stddev * correlation)


def bias(reference_values, values):
    """
    according to http://en.wikipedia.org/wiki/Bias_of_an_estimator
    """
    return np.mean(reference_values) - np.mean(values)


def unbiased_rmse(reference_values, values):
    squared_differences = ((values - np.mean(values)) - (reference_values - np.mean(reference_values))) ** 2
    squared_differences /= len(values)
    return np.sqrt(np.sum(squared_differences))


def correlation(reference_values, values):
    if len(np.unique(reference_values)) == 1 or len(np.unique(values)) == 1:
        return np.nan # if all reference or model values are equal, no sensible correlation coefficient can be computed.
    return np.corrcoef(values, reference_values)[0, 1]


def percentage_model_bias(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    return np.sum(reference_values - model_values) * 100 / np.sum(reference_values)


def reliability_index(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    n = 1 / len(reference_values)
    return np.exp(np.sqrt(n * np.sum(np.power(np.log10(reference_values / model_values), 2))))


def model_efficiency(reference_values, model_values):
    """
    Nash-Sutcliffe model efficiency according to MEECE D2.7 User guide and report outlining validation methodology
    """
    if len(np.unique(reference_values)) == 1:
        return np.nan # if all reference values are equal, no sensible model efficiency can be computed.
    return 1 - np.sum(np.power(reference_values - model_values, 2)) / np.sum(np.power(reference_values - np.mean(reference_values), 2))


def calculate_statistics(model_values, reference_values, model_name=None, ref_name=None, unit=None, config=None):
    """Calculate the statistics for the given reference and model arrays.
    It is recommended to provide model_name and ref_name in order to allow for meaningful output.
    """

    if config is None:
        config = get_default_config()

    model_percentiles = percentiles(model_values.ravel(), config.alpha, config.beta)
    ref_percentiles = percentiles(reference_values.ravel(), config.alpha, config.beta)
    model_minmax = minmax(model_values)
    ref_minmax = minmax(reference_values)
    stats = dict()
    stats['model_name'] = model_name
    stats['ref_name'] = ref_name
    stats['unit'] = unit
    stats['rmse'] = rmse(reference_values, model_values)
    stats['corrcoeff'] = correlation(reference_values, model_values)
    stats['unbiased_rmse'] = unbiased_rmse(reference_values, model_values)
    stats['normalised_rmse'] = normalised_rmse(reference_values, model_values, config.ddof, stats['corrcoeff'])
    stats['pbias'] = percentage_model_bias(reference_values, model_values)
    stats['bias'] = bias(reference_values, model_values)
    stats['reliability_index'] = reliability_index(reference_values, model_values)
    stats['model_efficiency'] = model_efficiency(reference_values, model_values)
    stats['mean'] = mean(model_values)
    stats['ref_mean'] = mean(reference_values)
    stats['stddev'] = stddev(model_values, config.ddof)
    stats['ref_stddev'] = stddev(reference_values, config.ddof)
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
