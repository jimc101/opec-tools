from numpy import sqrt, mean
import numpy

def computeRmsd(values, referenceValues):
    if len(values) != len(referenceValues):
        raise ValueError("len(values) != len(referenceValues)")
    squareErrors = (values - referenceValues) ** 2
    return sqrt(mean(squareErrors))

def computeBias(values, referenceValues):
    return mean(referenceValues) - mean(values)

def computeUnbiasedRmsd(values, referenceValues):
    squaredDifferences = ((values - mean(values)) - (referenceValues - mean(referenceValues))) ** 2
    squaredDifferences /= len(values)
    return sqrt(sum(squaredDifferences))

def computeCorrelation(values, referenceValues):
    return numpy.corrcoef(values, referenceValues)[0, 1]