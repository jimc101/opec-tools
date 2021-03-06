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

from argparse import ArgumentParser
import argparse
import logging
import shutil
import sys
import warnings
from zipfile import ZipFile
import os

import numpy as np
import numpy.ma as ma

from opec import processor, get_logging_formatter, utils
from opec.configuration import Configuration
from opec.matchup_engine import MatchupEngine
from opec.data import Data
from opec.output import Output

if not os.name == 'nt':
    import resource


class VariableMappingsParseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        result = []
        pair_string = values[0].replace('[', '').replace(']', '')
        pairs = pair_string.split(',')
        for pair in pairs:
            variables = pair.split(':')
            new_pair = [variables[0].lstrip().rstrip(), variables[1].lstrip().rstrip()]
            result.append(new_pair)
        setattr(namespace, self.dest, result)


class Formatter(argparse.RawDescriptionHelpFormatter):
    def _format_usage(self, usage, actions, groups, prefix):
        # clumsy way, but there's no native argparse support for what I do here
        # (what I do is: move <path> argument in usage description to beginning, where it belongs)
        the_format = super(argparse.RawDescriptionHelpFormatter, self)._format_usage(usage, actions, groups, prefix)
        the_format = the_format.replace('<path>', '')
        index = the_format.index('[-c')
        the_format = the_format[:index] + '| <path> ' + the_format[index:]
        return the_format

    def _format_action(self, action):
        # some cleanup of the help message
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        return parts.replace(' ,', ',').replace('  [ ...]', '')


class MyArgumentParser(ArgumentParser):
    def __init__(self):
        super(MyArgumentParser, self).__init__(formatter_class=Formatter)

    def error(self, message):
        raise ValueError(self.format_usage())


def parse_arguments(arguments):
    parser = MyArgumentParser()
    parser.add_argument('path', help='Path to the model output file', metavar='<path>')
    parser.add_argument('-c', '--config', help='Path to the configuration file', metavar='')
    parser.add_argument('-o', '--output_dir', help='Path to the target directory', metavar='')
    parser.add_argument('-p', '--prefix', help='Target prefix', metavar='')
    parser.add_argument('-v', '--variable_mappings', help='A list of variable mappings <var>:<ref_var>', metavar='',
                        nargs='+', action=VariableMappingsParseAction)
    parser.add_argument('-r', '--reference_file', help='An optional file containing the reference data', metavar='')
    return parser.parse_args(arguments)


def ref_stddev(statistics):
    return np.max(list(map(lambda x: x.get('ref_stddev'), statistics)))


def create_zip(target_files, config, file_handler, parsed_args):
    files_to_remove = []
    zipfile = ZipFile('%s/%sbenchmarks.zip' % (parsed_args.output_dir, config.target_prefix), 'w')
    logging.info('Creating zip file: %s' % zipfile.filename)
    for file in target_files:
        zipfile.write(file, os.path.basename(file))
        files_to_remove.append(file)
    if config.log_file is not None:
        logging.getLogger().removeHandler(file_handler)
        file_handler.flush()
        file_handler.close()
        log_file = '%s/%s' % (config.target_dir, config.log_file)
        zipfile.write(log_file, os.path.basename(config.log_file))
        files_to_remove.append(log_file)
    zipfile.close()
    for file in files_to_remove:
        os.remove(file)


def log_warning(msg, category, filename, lineno, file=None, line=None):
    msg = msg.args[0].replace('Warning: converting a masked element to nan.', 'converting a masked element to nan')
    logging.warn('%s in %s:%s' % (msg, filename, lineno))

#noinspection PyUnboundLocalVariable
def setup_logging(config):
    file_handler = None
    warnings.showwarning = log_warning
    if config.log_file is not None and config.log_level <= logging.CRITICAL:
        if not os.path.exists(config.target_dir):
            os.makedirs(config.target_dir)
        file_handler = logging.FileHandler('%s/%s' % (config.target_dir, config.log_file), 'w')
        file_handler.setFormatter(get_logging_formatter())
        logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(level=config.log_level)
    logging.info('Starting benchmark')
    return file_handler


def main():
    parsed_args = parse_arguments(sys.argv[1:])
    config = Configuration(properties_file_name=parsed_args.config, target_dir=parsed_args.output_dir,
                           target_prefix=parsed_args.prefix)
    file_handler = setup_logging(config)
    if parsed_args.reference_file is not None:
        data = Data(parsed_args.path, parsed_args.reference_file, config.max_cache_size)
    else:
        data = Data(parsed_args.path, max_cache_size=config.max_cache_size)

    output = Output(config=config)

    matchups = None
    if data.has_one_dim_ref_var():
        me = MatchupEngine(data, config)
        matchups = me.find_all_matchups()
        if not matchups:
            logging.warning('No matchups found. System will exit.')
            exit(0)
        if config.remove_empty_matchups:
            matchups = me.remove_empty_matchups(matchups)

    if not os.name == 'nt':
        logging.debug('Memory after matchups have been found: %s' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    matchup_count = 0 if matchups is None else len(matchups)
    collected_statistics = {}
    density_plot_files = []
    target_files = []
    density_plots = {}

    for (model_name, ref_name) in parsed_args.variable_mappings:
        unit = data.unit(model_name)
        is_gridded = len(data.get_reference_dimensions(ref_name)) > 1
        if is_gridded:
            reference_values, model_values = data.get_values(ref_name, model_name)
            matchup_count += ma.count(reference_values)
        else:
            reference_values, model_values = utils.extract_values(matchups, data, ref_name, model_name)
            reference_values, model_values = utils.harmonise(reference_values, model_values)
            logging.debug('Compressing ref-variable %s' % ref_name)
            reference_values = reference_values.compressed()
            logging.debug('Compressing model-variable %s' % model_name)
            model_values = model_values.compressed()

        logging.info('Calculating statistics for \'%s\' with \'%s\'' % (model_name, ref_name))
        stats = processor.calculate_statistics(model_values, reference_values, model_name, ref_name, unit, config)
        collected_statistics[(model_name, ref_name)] = stats

        if config.write_density_plots:
            axis_min = min(stats['min'], stats['ref_min'])
            axis_max = max(stats['p90'], stats['ref_p90'])
            logging.info('Creating density plot for \'%s\' and \'%s\'' % (model_name, ref_name))
            density_plots[model_name + ref_name] = output.density_plot(model_name, ref_name, model_values,
                                                                       reference_values, config.density_plot_log_scaled,
                                                                       None, axis_min, axis_max, data.unit(model_name))

    if not os.name == 'nt':
        logging.debug(
            'Memory after statistics have been computed: %s' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    if config.write_csv:
        csv_target_file = '%s/%sstatistics.csv' % (parsed_args.output_dir, config.target_prefix)
        target_files.append(csv_target_file)
        output.csv(data, parsed_args.variable_mappings, collected_statistics, matchup_count, matchups=matchups, source_file=parsed_args.path, target_file=csv_target_file)
        logging.info('CSV output written to \'%s\'' % csv_target_file)
        if matchups is not None:
            matchup_filename = '%s_matchups.csv' % os.path.splitext(csv_target_file)[0]
            logging.info('Matchups written to \'%s\'' % matchup_filename)
            target_files.append(matchup_filename)

    taylor_target_files = []
    if config.write_taylor_diagrams:
        taylor_target_file = '%s/%staylor.png' % (parsed_args.output_dir, config.target_prefix)
        written_taylor_diagrams, d = output.taylor(list(collected_statistics.values()), taylor_target_file)
        del d
        if written_taylor_diagrams:
            for written_taylor_diagram in written_taylor_diagrams:
                logging.info('Taylor diagram written to \'%s\'' % written_taylor_diagram)
                target_files.append(written_taylor_diagram)
                taylor_target_files.append(written_taylor_diagram)

    if config.write_density_plots:
        for (model_name, ref_name) in parsed_args.variable_mappings:
            density_target = '%s/density-%s-%s.png' % (parsed_args.output_dir, model_name, ref_name)
            density_plot_files.append(density_target)
            target_files.append(density_target)
            output.write_density_plot(density_plots[model_name + ref_name], density_target)
            logging.info('Density plot written to \'%s\'' % density_target)

    target_diagram_file = None
    if config.write_target_diagram:
        target_diagram_file = '%s/%starget.png' % (parsed_args.output_dir, config.target_prefix)
        output.target_diagram(list(collected_statistics.values()), target_diagram_file)
        logging.info('Target diagram written to \'%s\'' % target_diagram_file)
        target_files.append(target_diagram_file)

    if config.write_xhtml:
        xml_target_file = '%s/%sreport.xml' % (parsed_args.output_dir, config.target_prefix)
        path = str(os.path.dirname(os.path.realpath(__file__))) + '/../resources/'
        xsl = path + 'analysis-summary.xsl'
        css = path + 'styleset.css'
        xsl_target = '%s/%s' % (parsed_args.output_dir, os.path.basename(xsl))
        css_target = '%s/%s' % (parsed_args.output_dir, os.path.basename(css))
        output.xhtml(list(collected_statistics.values()), matchup_count, matchups, data, xml_target_file, taylor_target_files,
                     target_diagram_file, density_plot_files)
        logging.info('XHTML report written to \'%s\'' % xml_target_file)
        shutil.copy(xsl, parsed_args.output_dir)
        logging.info('XHTML support file written to \'%s/%s\'' % (parsed_args.output_dir, 'analysis-summary.xsl'))
        shutil.copy(css, parsed_args.output_dir)
        logging.info('XHTML support file written to \'%s/%s\'' % (parsed_args.output_dir, 'styleset.xsl'))
        target_files.append(xml_target_file)
        target_files.append(xsl_target)
        target_files.append(css_target)

    if config.zip:
        create_zip(target_files, config, file_handler, parsed_args)

    logging.info('End of process')


if __name__ == '__main__':
    main()
