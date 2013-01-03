import numpy as np
import numpy.ma as ma
import scipy.stats.mstats as mstats

def extract_values(matchups):
    reference_values = np.empty(len(matchups))
    model_values = np.empty(len(matchups))
    index = 0
    for matchup in matchups:
        reference_values[index] = matchup.ref_value
        model_values[index] = matchup.model_value
        index += 1
    return reference_values, model_values

def mean(values):
    return np.mean(values)

def stddev(values, ddof=0):
    return np.std(values, ddof=ddof)

def percentiles(values, alphap=1, betap=1):
    return mstats.mquantiles(values, [0.5, 0.9, 0.95], alphap, betap)

def minmax(values):
    return [np.min(values), np.max(values)]

def rmsd(reference_values, values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    if ma.count(values) != ma.count(reference_values):
        raise ValueError("len(values) != len(reference_values)")
    squareErrors = (values - reference_values) ** 2
    return np.sqrt(np.mean(squareErrors))

def bias(reference_values, values):
    """
    according to http://en.wikipedia.org/wiki/Bias_of_an_estimator
    """
    return np.mean(reference_values) - np.mean(values)

def unbiased_rmsd(reference_values, values):
    squared_differences = ((values - np.mean(values)) - (reference_values - np.mean(reference_values))) ** 2
    squared_differences /= ma.count(values)
    return np.sqrt(np.sum(squared_differences))

def correlation(reference_values, values):
    return ma.corrcoef(values, reference_values)[0, 1]

def percentage_model_bias(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    return np.sum(reference_values - model_values) * 100 / np.sum(reference_values)


def reliability_index(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    n = 1 / ma.count(reference_values)
    return np.exp(np.sqrt(n * np.sum(np.power(np.log10(reference_values / model_values), 2))))

def model_efficiency(reference_values, model_values):
    """
    Nash-Sutcliffe model efficiency according to MEECE D2.7 User guide and report outlining validation methodology
    """
    return 1 - np.sum(np.power(reference_values - model_values, 2)) / np.sum(np.power(reference_values - np.mean(reference_values), 2))

def create_masked_array(reference_values):
    false_mask = np.zeros(len(reference_values))
    if type(reference_values) is not ma.core.MaskedArray:
        reference_values = ma.array(reference_values, mask=false_mask)
    return reference_values

def harmonise(reference_values, model_values):
    reference_values = create_masked_array(reference_values)
    model_values = create_masked_array(model_values)
    reference_values.mask = reference_values.mask | model_values.mask
    model_values.mask = reference_values.mask | model_values.mask
    return reference_values, model_values

def basic_statistics(matchups=None, reference_values=None, model_values=None):
    if reference_values is None or model_values is None:
        reference_values, model_values = extract_values(matchups)
    reference_values, model_values = harmonise(reference_values, model_values)
    # todo - add parameter so that user can control how to calculate percentiles
    model_percentiles = percentiles(model_values)
    ref_percentiles = percentiles(reference_values)
    model_minmax = minmax(model_values)
    ref_minmax = minmax(reference_values)
    basic_stats = dict()
    basic_stats['rmsd'] = rmsd(reference_values, model_values)
    basic_stats['unbiased_rmsd'] = unbiased_rmsd(reference_values, model_values)
    basic_stats['pbias'] = percentage_model_bias(reference_values, model_values)
    basic_stats['bias'] = bias(reference_values, model_values)
    basic_stats['corrcoeff'] = correlation(reference_values, model_values)
    basic_stats['reliability_index'] = reliability_index(reference_values, model_values)
    basic_stats['model_efficiency'] = model_efficiency(reference_values, model_values)
    basic_stats['mean'] = mean(model_values)
    basic_stats['ref_mean'] = mean(reference_values)
    # todo - add parameter so that user can control how to calculate stddev
    basic_stats['stddev'] = stddev(model_values)
    basic_stats['ref_stddev'] = stddev(reference_values)
    basic_stats['median'] = model_percentiles[0]
    basic_stats['ref_median'] = ref_percentiles[0]
    basic_stats['p90'] = model_percentiles[1]
    basic_stats['ref_p90'] = ref_percentiles[1]
    basic_stats['p95'] = model_percentiles[2]
    basic_stats['ref_p95'] = ref_percentiles[2]
    basic_stats['min'] = model_minmax[0]
    basic_stats['ref_min'] = ref_minmax[0]
    basic_stats['max'] = model_minmax[1]
    basic_stats['ref_max'] = ref_minmax[1]
    return basic_stats

