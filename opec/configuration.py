# Copyright (C) 2013 Brockmann Consult GmbH (info@brockmann-consult.de)
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see http://www.gnu.org/licenses/gpl.html

import configparser
import logging
import os
import re

# needed because configparser.ConfigParser requires at least one section header in a properties file
# See http://stackoverflow.com/a/8555776 for source
def add_section_header(properties_file, header_name):
    yield '[{}]\n'.format(header_name)
    for line in properties_file:
        yield line

class Configuration(object):

    def __init__(self, alpha=None, beta=None, ddof=None, use_absolute_standard_deviation=None, time_delta=None, depth_delta=None,
                 latlon_delta=None, log_level=None, log_file=None, zip=None, show_negative_corrcoeff=None,
                 show_legends=None, target_dir=None, target_prefix=None, include_header=None, separator=None,
                 properties_file_name=None, write_taylor_diagrams=None, write_xhtml=None,
                 write_csv=None, write_density_plots=None, split_diagrams=None, write_target_diagram=None,
                 target_diagram_bounds=None, normalise_target_diagram=None, utilise_stddev_difference=None,
                 max_cache_size=None, density_plot_log_scaled=None, remove_empty_matchups=None):
        """
        Priority:
        1) what is passed as parameter
        2) what is found in file that has been passed as parameter
        3) what is found in default file
        """
        self.__read_properties(properties_file_name)
        self.__read_default_properties()

        if target_dir is None:
            target_dir = os.getcwd() # needed because if default shall be CWD, it cannot be put in the static config file

        self.__dict = {}
        self.__set(alpha, 'opec.algo.percentile.alpha', float)
        self.__set(beta, 'opec.algo.percentile.beta', float)
        self.__set(ddof, 'opec.algo.stddev.ddof', int)
        self.__set(time_delta, 'opec.matchup.time_delta', int)
        self.__set(depth_delta, 'opec.matchup.depth_delta', float)
        self.__set(latlon_delta, 'opec.matchup.latlon_delta', float)
        self.__set(log_level, 'opec.general.log_level', log_level_conv)
        self.__set(log_file, 'opec.general.log_file', log_file_conv)
        self.__set(zip, 'opec.output.zip', bool_conv)
        self.__set(show_negative_corrcoeff, 'opec.output.plot.taylor.show_negative_corrcoeff', bool_conv)
        self.__set(show_legends, 'opec.output.plot.show_legends', bool_conv)
        self.__set(target_dir, 'target_dir', str)
        self.__set(target_prefix, 'opec.output.target_prefix', str)
        self.__set(separator, 'opec.output.csv.separator', separator_conv)
        self.__set(include_header, 'opec.output.csv.include_header', bool_conv)
        self.__set(write_taylor_diagrams, 'opec.output.plot.taylor.write_taylor_diagrams', bool_conv)
        self.__set(write_xhtml, 'opec.output.xhtml.write_xhtml', bool_conv)
        self.__set(write_csv, 'opec.output.csv.write_csv', bool_conv)
        self.__set(use_absolute_standard_deviation, 'opec.output.plot.absolute_stddev', bool_conv)
        self.__set(write_density_plots, 'opec.output.plot.density.write_density_plots', bool_conv)
        self.__set(density_plot_log_scaled, 'opec.output.plot.density.log_scaled', bool_conv)
        self.__set(split_diagrams, 'opec.output.plot.taylor.split_diagrams', split_diagrams_conv('u'), 'opec.output.plot.split_on_unit')
        self.__set(split_diagrams, 'opec.output.plot.taylor.split_diagrams', split_diagrams_conv('n'), 'opec.output.plot.split_on_name')
        self.__set(write_target_diagram, 'opec.output.plot.target.write_target_diagram', bool_conv)
        self.__set(target_diagram_bounds, 'opec.output.plot.target.diagram_bounds', bounds_conv)
        self.__set(normalise_target_diagram, 'opec.output.plot.target.normalise_target_diagram', bool_conv)
        self.__set(utilise_stddev_difference, 'opec.output.plot.target.utilise_stddev_difference', bool_conv)
        self.__set(max_cache_size, 'opec.general.max_cache_size', int)
        self.__set(remove_empty_matchups, 'opec.output.remove_empty_matchups', bool_conv)


    def __set(self, value, name, converter, target_name=None):
        if value is not None:
             actual_value = value
        elif self.__config is not None and name in self.__config['dummy_section']:
            actual_value = self.__config['dummy_section'][name]
        else:
            actual_value = self.__default_config['dummy_section'][name]
        if target_name is None:
            target_name = name
        self.__dict[target_name] = converter(actual_value)


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
        default_properties_file = open(os.path.dirname(os.path.realpath(__file__)) + '/../resources/default.properties')
        self.__default_config.read_file(add_section_header(default_properties_file, 'dummy_section'))
        default_properties_file.close()


    def __alpha(self):
        return self.__dict['opec.algo.percentile.alpha']


    def __beta(self):
        return self.__dict['opec.algo.percentile.beta']


    def __ddof(self):
        return self.__dict['opec.algo.stddev.ddof']


    def __use_absolute_standard_deviation(self):
        return self.__dict['opec.output.plot.absolute_stddev']


    def __time_delta(self):
        return self.__dict['opec.matchup.time_delta']


    def __depth_delta(self):
        return self.__dict['opec.matchup.depth_delta']

    def __latlon_delta(self):
        return self.__dict['opec.matchup.latlon_delta']


    def __log_level(self):
        return self.__dict['opec.general.log_level']


    def __log_file(self):
        return self.__dict['opec.general.log_file']


    def __zip(self):
        return self.__dict['opec.output.zip']


    def __show_negative_corrcoeff(self):
        return self.__dict['opec.output.plot.taylor.show_negative_corrcoeff']


    def __show_legends(self):
        return self.__dict['opec.output.plot.show_legends']


    def __target_dir(self):
        return self.__dict['target_dir']


    def __target_prefix(self):
        return self.__dict['opec.output.target_prefix']


    def __include_header(self):
        return self.__dict['opec.output.csv.include_header']


    def __separator(self):
        return self.__dict['opec.output.csv.separator']


    def __write_taylor_diagrams(self):
        return self.__dict['opec.output.plot.taylor.write_taylor_diagrams']


    def __write_csv(self):
        return self.__dict['opec.output.csv.write_csv']


    def __write_xhtml(self):
        return self.__dict['opec.output.xhtml.write_xhtml']


    def __write_density_plots(self):
        return self.__dict['opec.output.plot.density.write_density_plots']


    def __split_on_unit(self):
        return self.__dict['opec.output.plot.split_on_unit']


    def __split_on_name(self):
        return self.__dict['opec.output.plot.split_on_name']


    def __write_target_diagram(self):
        return self.__dict['opec.output.plot.target.write_target_diagram']


    def __target_diagram_bounds(self):
        return self.__dict['opec.output.plot.target.diagram_bounds']


    def __normalise_target_diagram(self):
        return self.__dict['opec.output.plot.target.normalise_target_diagram']


    def __utilise_stddev_difference(self):
        return self.__dict['opec.output.plot.target.utilise_stddev_difference']


    def __max_cache_size(self):
        return self.__dict['opec.general.max_cache_size']


    def __density_plot_log_scaled(self):
        return self.__dict['opec.output.plot.density.log_scaled']


    def __remove_empty_matchups(self):
        return self.__dict['opec.output.remove_empty_matchups']


    alpha = property(__alpha)
    beta = property(__beta)
    ddof = property(__ddof)
    use_absolute_standard_deviation = property(__use_absolute_standard_deviation)
    time_delta = property(__time_delta)
    depth_delta = property(__depth_delta)
    latlon_delta = property(__latlon_delta)
    log_level = property(__log_level)
    log_file = property(__log_file)
    zip = property(__zip)
    show_negative_corrcoeff = property(__show_negative_corrcoeff)
    show_legends = property(__show_legends)
    target_dir = property(__target_dir)
    target_prefix = property(__target_prefix)
    include_header = property(__include_header)
    separator = property(__separator)
    write_taylor_diagrams = property(__write_taylor_diagrams)
    write_csv = property(__write_csv)
    write_xhtml = property(__write_xhtml)
    density_plot_log_scaled = property(__density_plot_log_scaled)
    write_density_plots = property(__write_density_plots)
    split_on_unit = property(__split_on_unit)
    split_on_name = property(__split_on_name)
    write_target_diagram = property(__write_target_diagram)
    target_diagram_bounds = property(__target_diagram_bounds)
    normalise_target_diagram = property(__normalise_target_diagram)
    utilise_stddev_difference = property(__utilise_stddev_difference)
    max_cache_size = property(__max_cache_size)
    remove_empty_matchups = property(__remove_empty_matchups)


def get_default_config():
    return Configuration()


def log_level_conv(value):
    log_level = value.upper()
    if log_level == 'DEBUG':
        return logging.DEBUG
    if log_level == 'INFO':
        return logging.INFO
    if log_level == 'WARNING':
        return logging.WARNING
    if log_level == 'CRITICAL' or log_level == 'FATAL':
        return logging.CRITICAL
    if log_level == 'DISABLED':
        return 100              # made-up logging value higher than max
    raise RuntimeError('Erroneous log level: %s' % value)


def bool_conv(value):
    return str(value).lower() == 'true'


def separator_conv(value):
    # I just didn't get escaped strings unescaped, so here's the low-tech version
    if value in ('\\t', 'tab', '\t'):
        return '\t'
    if value in ('\' \''):
        return ' '
    return value


def log_file_conv(value):
    return None if value.strip() == 'None' else value


def split_diagrams_conv(key):
    def shall_split_for_value(value):
        if len(value) > 0 and (not re.match('[un]', value) or len(value) > 3):
            raise ValueError('Illegal diagram split rule \'%s\', must comprise characters u and n at most.' % value)
        if key in value:
            return True
        return False
    return shall_split_for_value


def bounds_conv(value):
    if type(value) == list:
        return value
    if value == 'None':
        return None
    result = []
    for item in value.split(','):
        item = item.lstrip().rstrip().replace('[', '').replace(']', '')
        if item == 'None':
            result.append(None)
        else:
            result.append(float(item))
    return result
