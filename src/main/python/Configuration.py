import configparser

# needed because configparser.ConfigParser requires at least one section header in a properties file
# See http://stackoverflow.com/a/8555776 for source
def add_section_header(properties_file, header_name):
    yield '[{}]\n'.format(header_name)
    for line in properties_file:
        yield line


class Configuration(object):

    def __init__(self, alpha=None, beta=None, ddof=None, macro_pixel_size=None, geo_delta=None, time_delta=None,
                 depth_delta=None, log_level=None, zip=None, show_negative_corrcoeff=None, show_legend=None, properties_file_name=None):
        """
        Priority:
        1) what is passed as parameter
        2) what is found in file that has been passed as parameter
        3) what is found in default file
        """
        self.__read_properties(properties_file_name)
        self.__read_default_properties()

        self.__dict = {}
        self.__set(alpha, 'alpha')
        self.__set(beta, 'beta')
        self.__set(ddof, 'ddof')
        self.__set(macro_pixel_size, 'macro_pixel_size')
        self.__set(geo_delta, 'geo_delta')
        self.__set(time_delta, 'time_delta')
        self.__set(depth_delta, 'depth_delta')
        self.__set(log_level, 'log_level')
        self.__set(zip, 'zip')
        self.__set(show_negative_corrcoeff, 'show_negative_corrcoeff')
        self.__set(show_legend, 'show_legend')

    def __set(self, value, name):
        if value is not None:
            self.__dict[name] = value
        elif self.__config is not None and name in self.__config['dummy_section']:
            self.__dict[name] = self.__config['dummy_section'][name]
        else:
            self.__dict[name] = self.__default_config['dummy_section'][name]

    def __read_properties(self, properties_file_name):
        if properties_file_name is not None:
            self.__config = configparser.ConfigParser()
            properties_file = open(properties_file_name)
            self.__config.read_file(add_section_header(properties_file, 'dummy_section'))
            properties_file.close()
        else:
            self.__config = None

    def __read_default_properties(self):
        self.__default_config = configparser.ConfigParser()
        default_properties_file = open('../../../default.properties')
        self.__default_config.read_file(add_section_header(default_properties_file, 'dummy_section'))
        default_properties_file.close()

    def __alpha(self):
        return float(self.__dict['alpha'])

    def __beta(self):
        return float(self.__dict['beta'])

    def __ddof(self):
        return int(self.__dict['ddof'])

    def __macro_pixel_size(self):
        return int(self.__dict['macro_pixel_size'])

    def __geo_delta(self):
        return float(self.__dict['geo_delta'])

    def __time_delta(self):
        return int(self.__dict['time_delta'])

    def __depth_delta(self):
        return float(self.__dict['depth_delta'])

    def __log_level(self):
        return self.__dict['log_level'].upper()

    def __zip(self):
        return self.__dict['zip'].lower() == 'true'

    def __show_negative_corrcoeff(self):
        return self.__dict['show_negative_corrcoeff'].lower() == 'true'

    def __show_legend(self):
        return str(self.__dict['show_legend']).lower() == 'true'

    alpha = property(__alpha)
    beta = property(__beta)
    ddof = property(__ddof)
    macro_pixel_size = property(__macro_pixel_size)
    geo_delta = property(__geo_delta)
    time_delta = property(__time_delta)
    depth_delta = property(__depth_delta)
    log_level = property(__log_level)
    zip = property(__zip)
    show_negative_corrcoeff = property(__show_negative_corrcoeff)
    show_legend = property(__show_legend)

def get_default_config():
    return Configuration()