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

    alpha = property(alpha)
    beta = property(beta)
    ddof = property(ddof)
    macro_pixel_size = property(macro_pixel_size)
    geo_delta = property(geo_delta)
    time_delta = property(time_delta)
    depth_delta = property(depth_delta)

def get_default_config():
    return Configuration()