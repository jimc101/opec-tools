class Matchup(object):

    def __init__(self, ref_variable_name, model_variable_name, ref_value, model_value, ref_lat, ref_lon, ref_time, lat_delta, lon_delta, time_delta, ref_depth=None, depth_delta=None):
        """
       Constructs a matchup object.

       @param ref_variable_name: The name of the variable.

       @param ref_value: The value of the reference measurement.

       @param model_value: The matching value of the model.

       @param ref_lat the reference latitude.

       @param ref_lon the reference longitude.

       @param ref_time the reference time.

       @param ref_depth the reference depth; None by default.

       @param lat_delta the difference between reference latitude and the model latitude.

       @param lon_delta the difference between reference longitude and the model longitude.

       @param time_delta the difference between reference time and the model time.

       @param depth_delta the difference between reference depth and the model depth; None by default.
        """

        self.__ref_variable_name = ref_variable_name
        self.__model_variable_name = model_variable_name
        self.__ref_value = ref_value
        self.__model_value = model_value
        self.__ref_lat = ref_lat
        self.__ref_lon = ref_lon
        self.__ref_time = ref_time
        self.__ref_depth = ref_depth
        self.__lat_delta = lat_delta
        self.__lon_delta = lon_delta
        self.__time_delta = time_delta
        self.__depth_delta = depth_delta


    def get_ref_value(self):
        return self.__ref_value

    def get_ref_lat(self):
        return self.__ref_lat

    def get_ref_lon(self):
        return self.__ref_lon

    def get_ref_time(self):
        return self.__ref_time

    def get_ref_depth(self):
        return self.__ref_depth

    def get_lat_delta(self):
        return self.__lat_delta

    def get_lon_delta(self):
        return self.__lon_delta

    def get_time_delta(self):
        return self.__time_delta

    def get_depth_delta(self):
        return self.__depth_delta

    def get_model_value(self):
        return self.__model_value

    ref_value = property(get_ref_value)
    ref_lat = property(get_ref_lat)
    ref_lon = property(get_ref_lon)
    ref_time = property(get_ref_time)
    ref_depth = property(get_ref_depth)
    lat_delta = property(get_lat_delta)
    lon_delta = property(get_lon_delta)
    time_delta = property(get_time_delta)
    depth_delta = property(get_depth_delta)
    model_value = property(get_model_value)
