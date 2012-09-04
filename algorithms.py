from numpy import sqrt, mean

def computeRmsd(values, referenceValue):
    squareErrors = (values - referenceValue) ** 2
    return sqrt(mean(squareErrors))

def computeBias(values, referenceValue):
    return referenceValue - mean(values)

def computeUnbiasedRmsd(values):
    squaredDifferences = (values - mean(values)) ** 2
    squaredDifferences /= len(values)
    return sqrt(sum(squaredDifferences))