from argparse import ArgumentParser
import os

def parse_arguments(arguments):
    parser = MyArgumentParser(description='Process some integers.')
    parser.add_argument('-a', help='Path to the algorithm specification file', metavar='Algorithm specification file', default=DefaultAlgorithmSpec())
    parser.add_argument('-o', help='Path to the target directory', metavar='Target directory', default=os.getcwd())
    parser.add_argument('-p', help='Target prefix', metavar='Target prefix', default='benchmark_')
    parser.add_argument('path', help='Path to the model output file', metavar='<path>')
    return parser.parse_args(arguments)

class MyArgumentParser(ArgumentParser):

    def error(self, message):
        raise ValueError(self.format_usage())

class DefaultAlgorithmSpec(object):
    # todo - implement
    pass