from numpy import sqrt, mean

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
    meanValues = mean(values)
    meanReference = mean(referenceValues)

    temp = (values - meanValues) * (referenceValues - meanReference)
    numerator = sum(temp)
    denominator = sqrt(sum((values - meanValues) ** 2) * sum((referenceValues - meanReference) ** 2))
    return numerator / denominator