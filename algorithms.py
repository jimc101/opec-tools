from numpy import sqrt, mean

def rootMeanSquareDeviation(modelValues, referenceValue):
    squareErrors = (modelValues - referenceValue) ** 2
    return sqrt(mean(squareErrors))
