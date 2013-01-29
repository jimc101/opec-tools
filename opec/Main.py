from argparse import ArgumentParser
import argparse
import logging
import shutil
import sys
import warnings
from zipfile import ZipFile
from opec import Processor, Utils
from opec.Configuration import Configuration
from opec.MatchupEngine import MatchupEngine
from opec.Data import Data
from opec.Output import Output
import numpy as np
import os

class VariableMappingsParseAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        result = []
        pairs = values[0].lstrip().split(',')
        for pair in pairs:
            vars = pair.split(':')
            new_pair = [vars[0], vars[1]]
            result.append(new_pair)
        setattr(namespace, self.dest, result)

class MyArgumentParser(ArgumentParser):

    def error(self, message):
        raise ValueError(self.format_usage())

def parse_arguments(arguments):
    parser = MyArgumentParser(description='Process some integers.')
    parser.add_argument('-a', help='Path to the algorithm specification file', metavar='Algorithm specification file')
    parser.add_argument('-o', help='Path to the target directory', metavar='Target directory')
    parser.add_argument('-p', help='Target prefix', metavar='Target prefix')
    parser.add_argument('-v', help='A list of variable mappings', metavar='Variable mapping', nargs='+', action=VariableMappingsParseAction)
    parser.add_argument('-r', help='An optional file containing the reference data', metavar='Reference data file')
    parser.add_argument('path', help='Path to the model output file', metavar='<path>')
    return parser.parse_args(arguments)

def ref_stddev(statistics):
    return np.max(list(map(lambda x: x.get('ref_stddev'), statistics)))

def create_zip(target_files, config, file_handler, parsed_args):
    files_to_remove = []
    zipfile = ZipFile('%s\\%sbenchmarks.zip' % (parsed_args.o, config.target_prefix), 'w')
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
        file_handler.setFormatter(Utils.get_logging_formatter())
        logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(level=config.log_level)
    logging.info('Starting benchmark')
    return file_handler

def main():
    parsed_args = parse_arguments(sys.argv[1:])
    config = Configuration(properties_file_name=parsed_args.a, target_dir=parsed_args.o, target_prefix=parsed_args.p)
    file_handler = setup_logging(config)
    if parsed_args.r is not None:
        data = Data(parsed_args.path, parsed_args.r)
    else:
        data = Data(parsed_args.path)
    me = MatchupEngine(data, config)
    collected_statistics = []
    output = Output(config=config, source_file=parsed_args.path)
    matchups = me.find_all_matchups()

    for pair in parsed_args.v:
        unit = data.unit(pair[0])
        stats = Processor.calculate_statistics(matchups=matchups, config=config, model_name=pair[1], ref_name=pair[0], unit=unit)
        collected_statistics.append(stats)

    target_files = []
    if config.write_csv:
        for pair, stats in zip(parsed_args.v, collected_statistics):
            csv_target_file = '%s\\%s%s_statistics.csv' % (parsed_args.o, config.target_prefix, pair[0])
            target_files.append(csv_target_file)
            output.csv(stats, variable_name=pair[1], ref_variable_name=pair[0], matchups=matchups, target_file=csv_target_file)
            logging.info('CSV output written to \'%s\'' % csv_target_file)
            if matchups and config.separate_matchups:
                matchup_filename = '%s_matchups.csv' % os.path.splitext(csv_target_file)[0]
                logging.info('Matchups written to \'%s\'' % matchup_filename)
                target_files.append(matchup_filename)

    taylor_target_files = []
    if config.write_taylor_diagrams:
        taylor_target_file = '%s\\%staylor.png' % (parsed_args.o, config.target_prefix)
        written_taylor_diagrams = output.taylor(collected_statistics, taylor_target_file)
        if written_taylor_diagrams:
            for written_taylor_diagram in written_taylor_diagrams:
                logging.info('Taylor diagram written to \'%s\'' % written_taylor_diagram)
                target_files.append(written_taylor_diagram)
                taylor_target_files.append(written_taylor_diagram)
        else:
            taylor_target_file = None

    scatter_plot_files = []
    if config.write_scatter_plots:
        for pair in parsed_args.v:
            scatter_target = '%s/scatter-%s-%s.png' % (parsed_args.o, pair[0], pair[1])
            scatter_plot_files.append(scatter_target)
            target_files.append(scatter_target)
            output.scatter_plot(matchups, pair[0], pair[1], scatter_target, data.unit(pair[0]))

    if config.write_xhtml:
        xml_target_file = '%s\\%sreport.xml' % (parsed_args.o, config.target_prefix)
        xsl = 'resources/analysis-summary.xsl'
        css = 'resources/styleset.css'
        xsl_target = '%s/%s' % (parsed_args.o, os.path.basename(xsl))
        css_target = '%s/%s' % (parsed_args.o, os.path.basename(css))
        output.xhtml(collected_statistics, matchups, xml_target_file, taylor_target_files, scatter_plot_files)
        logging.info('XHTML report written to \'%s\'' % xml_target_file)
        shutil.copy(xsl, parsed_args.o)
        logging.info('XHTML support file written to \'%s/%s\'' % (parsed_args.o, 'analysis-summary.xsl'))
        shutil.copy(css, parsed_args.o)
        logging.info('XHTML support file written to \'%s/%s\'' % (parsed_args.o, 'styleset.xsl'))
        target_files.append(xml_target_file)
        target_files.append(xsl_target)
        target_files.append(css_target)

    if config.zip:
        create_zip(target_files, config, file_handler, parsed_args)

    logging.info('End of process')

if __name__ == '__main__':
    main()