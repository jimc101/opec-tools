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

from opec import Processor
from opec.Configuration import Configuration
from opec.Data import Data
from opec.MatchupEngine import MatchupEngine
from opec.Output import Output

def load(filename, ref_filename=None, config=None):
    """
    Returns an abstraction view on the data from the given input file.
    @param filename: the source file.
    @param ref_filename: the file containing the reference data; if None, the reference data is assumed to be in the source file.
    @return: a 'Data' object.
    """
    return Data(filename, ref_filename, config.max_cache_size)


def create_config(filename):
    """
    Returns a configuration according to the properties file.
    @param filename: the path to the properties file used to load configuration from.
    @return: an object of type 'Configuration'.
    """
    return Configuration(properties_file_name=filename)


def calculate_statistics(model_name, ref_name, data, config=None):
    """
    Calculates the statistics for the given model and reference variables located in the data file. Calculation will be
    performed according to the provided configuration.
    @param model_name: the name of the model variable.
    @param ref_name: the name of the reference variable.
    @param data: the input data object.
    @param config: the optional configuration.
    @return: a dictionary of statistics.
    """
    me = MatchupEngine(data, config)
    matchups = me.find_all_matchups()
    return calculate_statistics_from_matchups(matchups, model_name, ref_name, config=None)


def calculate_statistics_from_matchups(matchups, model_name, ref_name, config=None):
    """
    Calculates the statistics for the given matchups and model and reference variable. Calculation will be
    performed according to the provided configuration.
    @param matchups: an iterable of 'Matchup' objects.
    @param model_name: the name of the model variable.
    @param ref_name: the name of the reference variable.
    @param config: the optional configuration.
    @return: a dictionary of statistics.
    """
    return Processor.calculate_statistics(matchups, model_name, ref_name, config=config)


def calculate_statistics_from_values(model_values, ref_values, config=None):
    """
    Calculates the statistics for two given numpy arrays; the first is considered the model data, the second is
    considered the reference data. Calculation will be performed according to the provided configuration. Note that the
    condition len(model_values) == len(ref_values) must hold.
    @param model_values: numpy array containing the model values.
    @param ref_values: numpy array containing the reference values.
    @param config: the optional configuration.
    @return: a dictionary of statistics.
    """
    return Processor.calculate_statistics(model_values=model_values, reference_values=ref_values, config=config)


def get_matchups(data, config=None):
    """
    Returns all matchups in the given dataset.
    @param data: the source data file.
    @param config: the optional configuration.
    @return: all matchups.
    """
    me = MatchupEngine(data, config)
    return me.find_all_matchups()


def extract_values(model_name, ref_name, data, config=None):
    """
    Extracts the matchups for the given data and returns the reference values and the model values for the given
    variables.
    @param model_name: the name of the model variable.
    @param ref_name: the name of the reference variable.
    @param data: the source data file.
    @param config: the optional configuration.
    @return: two numpy arrays: reference_values, model_values
    """
    ma = get_matchups(data, config)
    return extract_values_from_matchups(ma, model_name, ref_name)


def extract_values_from_matchups(matchups, model_name, ref_name):
    """
    Returns the reference values and the model values for the given variables in the given matchups.
    @param matchups: the matchups from which to extract the data.
    @param model_name: the name of the model variable.
    @param ref_name: the name of the reference variable.
    @return: two numpy arrays: reference_values, model_values
    """
    return Processor.extract_values(matchups, ref_name, model_name)


def write_csv(statistics, model_name, ref_name, matchups, target_file=None, config=None):
    """
    Returns the given statistics as CSV string; writes this string if target_file is provided.
    @param statistics: a dictionary containing all statistics.
    @param model_name: the model variable name.
    @param ref_name: the reference variable name.
    @param matchups: the matchups.
    @param target_file: the optional target file; if not None, result string will be written to that file.
    @param config: the optional configuration.
    @return: the given statistics as CSV string.
    """
    op = Output(config=config)
    op.csv(statistics, model_name, ref_name, matchups, target_file)


def taylor_diagrams(statistics, target_file=None, config=None):
    """
    Creates the taylor diagrams derived from the statistics and possibly writes them to the given target file.
    @param statistics: an iterable of statistics to write taylor diagrams for.
    @param target_file: the basename for the file where to write the taylor diagrams. If None, nothing will be written.
    @param config: the optional configuration.
    @return: a list of the taylor diagrams.
    """
    op = Output(config=config)
    t, diagrams = op.taylor(statistics, target_file)
    return diagrams


def target_diagram(statistics, target_file=None, config=None):
    """
    Creates the target diagram derived from the statistics and possibly writes it to the given target file.
    @param statistics: An iterable of statistics to write the target diagram for.
    @param target_file: the name of the target diagram file. If None, nothing will be written.
    @param config: the optional configuration.
    @return: the target diagram.
    """
    op = Output(config=config)
    return op.target_diagram(statistics, target_file)


def scatter_plot(matchups, model_name, ref_name, unit=None, target_file=None, config=None):
    """
    Creates the scatter plot for the given matchups and variables and possible writes it to the given target file.
    @param matchups: the matchups to create a scatter plot for.
    @param model_name: the name of the model variable.
    @param ref_name: the name of the reference variable.
    @param unit: the optional unit of the variables.
    @param target_file: the optional target diagram file. If None, nothing will be written.
    @param config: the optional configuration.
    @return: the scatter plot.
    """
    op = Output(config=config)
    return op.scatter_plot(matchups, ref_name, model_name, target_file, unit)


def write_xhtml_report(statistics_list, matchups, target_file, taylor_target_files=None, target_diagram_file=None, scatter_plot_files=None, config=None):
    """
    Writes the xhtml report to the given target file.
    @param statistics_list: the list of statistics to mention in the report.
    @param matchups: the matchups the statistics have been calculated for.
    @param target_file: the target xhtml file.
    @param taylor_target_files: the optional paths to the taylor diagrams.
    @param target_diagram_file: the optional paths to the target diagram.
    @param scatter_plot_files: the optional paths to the scatter plots.
    @param config: the optional configuration.
    @return: None.
    """
    op = Output(config=config)
    op.xhtml(statistics_list, matchups, target_file, taylor_target_files, target_diagram_file, scatter_plot_files)