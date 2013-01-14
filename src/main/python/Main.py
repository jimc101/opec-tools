from argparse import ArgumentParser
import argparse
import logging
import sys
from zipfile import ZipFile
from src.main.python import Processor
from src.main.python.Configuration import Configuration
from src.main.python.Data import Data
from src.main.python.MatchupEngine import MatchupEngine
from src.main.python.Output import Output
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

def main():
    parsed_args = parse_arguments(sys.argv[1:])
    config = Configuration(properties_file_name=parsed_args.a, target_dir=parsed_args.o, target_prefix=parsed_args.p)
    logging.basicConfig(level=config.log_level)
    logging.info('Starting benchmark')
    data = Data(parsed_args.path)
    me = MatchupEngine(data, config)
    collected_statistics = []
    collected_csv_target_files = []
    output = Output(config=config, source_file=parsed_args.path)
    for pair in parsed_args.v:
        matchups = me.find_all_matchups(pair[0], pair[1])
        stats = Processor.calculate_statistics(matchups=matchups, config=config, model_name=pair[1], ref_name=pair[0])
        collected_statistics.append(stats)
        csv_target_file = '%s\\%s%s_statistics.csv' % (parsed_args.o, config.target_prefix, pair[0])
        collected_csv_target_files.append(csv_target_file)
        output.csv(stats, target_file=csv_target_file, matchup_count=len(matchups), ref_variable_name=pair[0], variable_name=pair[1])
        logging.info('csv output written to \'%s\'' % csv_target_file)

    if config.write_taylor_diagram:
        taylor_target_file = '%s\\%staylor.png' % (parsed_args.o, config.target_prefix)
        output.taylor(taylor_target_file, collected_statistics)
        logging.info('taylor diagram written to \'%s\'' % taylor_target_file)

    if config.zip:
        zipfile = ZipFile('%s\\%sbenchmarks.zip' % (parsed_args.o, config.target_prefix), 'w')
        for file in collected_csv_target_files:
            zipfile.write(file, os.path.basename(file))
        if config.write_taylor_diagram:
            zipfile.write(taylor_target_file, os.path.basename(taylor_target_file))
        zipfile.close()
        for file in collected_csv_target_files:
            os.remove(file)
        if config.write_taylor_diagram:
            os.remove(taylor_target_file)

if __name__ == '__main__':
    main()