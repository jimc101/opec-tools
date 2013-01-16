from argparse import ArgumentParser
import argparse
import logging
import sys
from zipfile import ZipFile
from opec import Processor
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
    parser.add_argument('path', help='Path to the model output file', metavar='<path>')
    return parser.parse_args(arguments)

def ref_stddev(statistics):
    return np.max(list(map(lambda x: x.get('ref_stddev'), statistics)))

def zip(collected_csv_target_files, config, file_handler, log_file, parsed_args, taylor_target_file):
    zipped_files = []
    zipfile = ZipFile('%s\\%sbenchmarks.zip' % (parsed_args.o, config.target_prefix), 'w')
    logging.info('Creating zip file: %s' % zipfile.filename)
    for file in collected_csv_target_files:
        zipfile.write(file, os.path.basename(file))
        zipped_files.append(file)
    if config.write_taylor_diagram:
        zipfile.write(taylor_target_file, os.path.basename(taylor_target_file))
        zipped_files.append(taylor_target_file)
    if config.write_log_file:
        logging.getLogger().removeHandler(file_handler)
        file_handler.flush()
        file_handler.close()
        zipfile.write(log_file, os.path.basename(log_file))
        zipped_files.append(log_file)
    zipfile.close()
    for file in zipped_files:
        os.remove(file)

#noinspection PyUnboundLocalVariable
def setup_logging(config):
    if config.write_log_file:
        log_file = config.log_file if config.log_file is not None else '%s/benchmarking.log' % config.target_dir
        file_handler = logging.FileHandler(log_file)
        logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(level=config.log_level)
    logging.info('Starting benchmark')
    return file_handler, log_file

#noinspection PyUnboundLocalVariable
def main():
    parsed_args = parse_arguments(sys.argv[1:])
    config = Configuration(properties_file_name=parsed_args.a, target_dir=parsed_args.o, target_prefix=parsed_args.p)
    file_handler, log_file = setup_logging(config)
    data = Data(parsed_args.path)
    me = MatchupEngine(data, config)
    collected_statistics = []
    collected_csv_target_files = []
    output = Output(config=config, source_file=parsed_args.path)
    for pair in parsed_args.v:
        matchups = me.find_all_matchups()
        stats = Processor.calculate_statistics(matchups=matchups, config=config, model_name=pair[1], ref_name=pair[0], data=data)
        collected_statistics.append(stats)
        csv_target_file = '%s\\%s%s_statistics.csv' % (parsed_args.o, config.target_prefix, pair[0])
        collected_csv_target_files.append(csv_target_file)
        output.csv(stats, target_file=csv_target_file, matchup_count=len(matchups), ref_variable_name=pair[0], variable_name=pair[1])
        logging.info('CSV output written to \'%s\'' % csv_target_file)

    if config.write_taylor_diagram:
        taylor_target_file = '%s\\%staylor.png' % (parsed_args.o, config.target_prefix)
        output.taylor(collected_statistics, taylor_target_file)
        logging.info('Taylor diagram written to \'%s\'' % taylor_target_file)

    if config.zip:
        zip(collected_csv_target_files, config, file_handler, log_file, parsed_args, taylor_target_file)

    logging.info('End of process')

if __name__ == '__main__':
    main()