from argparse import ArgumentParser
import argparse
import logging
import sys
from src.main.python import Processor
from src.main.python.Configuration import Configuration
from src.main.python.Data import Data
from src.main.python.MatchupEngine import MatchupEngine
from src.main.python.Output import Output

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

def main():
    parsed_args = parse_arguments(sys.argv[1:])
    config = Configuration(properties_file_name=parsed_args.a, target_dir=parsed_args.o, target_prefix=parsed_args.p)
    logging.basicConfig(level=config.log_level)
    logging.debug('Starting benchmark')
    data = Data(parsed_args.path)
    me = MatchupEngine(data, config)
    for pair in parsed_args.v:
        matchups = me.find_all_matchups(pair[0], pair[1])
        stats = Processor.calculate_statistics(matchups=matchups, config=config, model_name=parsed_args.path)
        logging.debug('having stats')
        output = Output(statistics=stats, ref_variable_name=pair[0], variable_name=pair[1], config=config, matchup_count=len(matchups), source_file=parsed_args.path)
        logging.debug('having output')
        output.csv(config.include_header, config.separator, target_file='%s\\%s%s_statistics.csv' % (parsed_args.o, config.target_prefix, pair[0]))
        logging.debug('output done')

if __name__ == '__main__':
    main()
