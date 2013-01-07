import configparser

# needed because configparser.ConfigParser requires at least one section header in a properties file
# See http://stackoverflow.com/a/8555776 for source
def add_section_header(properties_file, header_name):
    yield '[{}]\n'.format(header_name)
    for line in properties_file:
        yield line


class Configuration(object):

    def __init__(self, alpha=None, beta=None, ddof=None, macro_pixel_size=None, geo_delta=None, time_delta=None,
                 depth_delta=None, log_level=None, zip=None, properties_file_name=None):
        """
        Priority:
        1) what is passed as parameter
        2) what is found in file that has been passed as parameter
        3) what is found in default file
        """
        self.read_properties(properties_file_name)
        self.read_default_properties()

        self.__dict = {}
        self.set(alpha, 'alpha')
        self.set(beta, 'beta')
        self.set(ddof, 'ddof')
        self.set(macro_pixel_size, 'macro_pixel_size')
        self.set(geo_delta, 'geo_delta')
        self.set(time_delta, 'time_delta')
        self.set(depth_delta, 'depth_delta')
        self.set(log_level, 'log_level')
        self.set(zip, 'zip')

    def set(self, value, name):
        if value is not None:
            self.__dict[name] = value
        elif self.__config is not None and name in self.__config['dummy_section']:
            self.__dict[name] = self.__config['dummy_section'][name]
        else:
            self.__dict[name] = self.__default_config['dummy_section'][name]

    def read_properties(self, properties_file_name):
        if properties_file_name is not None:
            self.__config = configparser.ConfigParser()
            properties_file = open(properties_file_name)
            self.__config.read_file(add_section_header(properties_file, 'dummy_section'))
            properties_file.close()
        else:
            self.__config = None

    def read_default_properties(self):
        self.__default_config = configparser.ConfigParser()
        default_properties_file = open('../../../default.properties')
        self.__default_config.read_file(add_section_header(default_properties_file, 'dummy_section'))
        default_properties_file.close()

    def alpha(self):
        return float(self.__dict['alpha'])

    def beta(self):
        return float(self.__dict['beta'])

    def ddof(self):
        return int(self.__dict['ddof'])

    def macro_pixel_size(self):
        return int(self.__dict['macro_pixel_size'])

    def geo_delta(self):
        return float(self.__dict['geo_delta'])

    def time_delta(self):
        return int(self.__dict['time_delta'])

    def depth_delta(self):
        return float(self.__dict['depth_delta'])

    def log_level(self):
        return self.__dict['log_level'].upper()

    def zip(self):
        return self.__dict['zip'].lower() == 'true'

    alpha = property(alpha)
    beta = property(beta)
    ddof = property(ddof)
    macro_pixel_size = property(macro_pixel_size)
    geo_delta = property(geo_delta)
    time_delta = property(time_delta)
    depth_delta = property(depth_delta)
    log_level = property(log_level)
    zip = property(zip)

def get_default_config():
    return Configuration()