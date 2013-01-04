class Configuration(object):

    # todo -- replace this by reading config file
    def __init__(self, alpha=0.2, beta=0.2, ddof=3, macro_pixel_size=3, geo_delta=12, time_delta=86400, depth_delta=10):
        self.__alpha = alpha
        self.__beta = beta
        self.__ddof = ddof
        self.__macro_pixel_size = macro_pixel_size
        self.__geo_delta = geo_delta
        self.__time_delta = time_delta
        self.__depth_delta = depth_delta

    def alpha(self):
        return self.__alpha

    def beta(self):
        return self.__beta

    def ddof(self):
        return self.__ddof

    def macro_pixel_size(self):
        return self.__macro_pixel_size

    def geo_delta(self):
        return self.__geo_delta

    def time_delta(self):
        return self.__time_delta

    def depth_delta(self):
        return self.__depth_delta

    def set_alpha(self, alpha):
        self.__alpha = alpha

    def set_beta(self, beta):
        self.__beta = beta

    def set_ddof(self, ddof):
        self.__ddof = ddof

    def set_macro_pixel_size(self, macro_pixel_size):
        self.__macro_pixel_size = macro_pixel_size

    def set_geo_delta(self, geo_delta):
        self.__geo_delta = geo_delta

    def set_time_delta(self, time_delta):
        self.__time_delta = time_delta

    def set_depth_delta(self, depth_delta):
        self.__depth_delta = depth_delta

    alpha = property(alpha, set_alpha)
    beta = property(beta, set_beta)
    ddof = property(ddof, set_ddof)
    macro_pixel_size = property(macro_pixel_size, set_macro_pixel_size)
    geo_delta = property(geo_delta, set_geo_delta)
    time_delta = property(time_delta, set_time_delta)
    depth_delta = property(depth_delta, set_depth_delta)

    def set_to_default(self):
        # todo -- replace this by reading config file
        self.alpha = 0.2
        self.beta = 0.2
        self.ddof = 1

# singleton-like implementation -- sufficient for the moment, maybe something more sophisticated is needed later
def global_config():
    return __global_config()

def __global_config(c=Configuration()):
    return c