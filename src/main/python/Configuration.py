class Configuration(object):

    # todo -- replace this by reading config file
    def __init__(self, alpha=0.2, beta=0.2, ddof=3):
        self.__alpha = alpha
        self.__beta = beta
        self.__ddof = ddof

    def alpha(self):
        return self.__alpha

    def beta(self):
        return self.__beta

    def ddof(self):
        return self.__ddof

    def set_alpha(self, alpha):
        self.__alpha = alpha

    def set_beta(self, beta):
        self.__beta = beta

    def set_ddof(self, ddof):
        self.__ddof = ddof

    alpha = property(alpha, set_alpha)
    beta = property(beta, set_beta)
    ddof = property(ddof, set_ddof)

    def reload(self):
        # todo -- replace this by reading config file
        self.alpha = 0.2
        self.beta = 0.2
        self.ddof = 1

# singleton-like implementation -- sufficient for the moment, maybe something more sophisticated is needed later
def global_config():
    return __global_config()

def __global_config(c=Configuration()):
    return c