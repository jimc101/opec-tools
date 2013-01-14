from datetime import datetime
import os
from src.main.python import Plotter
from src.main.python.Configuration import get_default_config

class Output(object):

    def __init__(self, **kwargs):
        """Constructs a new instance of Output.

        Keyword arguments:
            config -- the configuration the processors and matchup engine have been run with (optional)
            source_file -- a reference to the file the benchmarks were computed on (optional)
        """
        self.config = kwargs['config'] if 'config' in kwargs.keys() else get_default_config()
        self.source_file = kwargs['source_file'] if 'source_file' in kwargs.keys() else None

    def csv(self, statistics, target_file=None, **kwargs):
        """Outputs the statistics to CSV.

        Keyword arguments:
            variable_name -- the model variable name (optional)
            ref_variable_name -- the reference variable name (optional)
            matchup_count -- the number of matchups (optional)
            target_file -- if specified, the CSV will be written to the file. (optional)
        """

        variable_name = kwargs['variable_name'] if 'variable_name' in kwargs.keys() else None
        ref_variable_name = kwargs['ref_variable_name'] if 'ref_variable_name' in kwargs.keys() else None
        matchup_count = kwargs['matchup_count'] if 'matchup_count' in kwargs.keys() else None
        include_header = self.config.include_header
        separator = self.config.separator

        lines = []
        if include_header:
            self.__write_header(lines)
        lines.append(separator.join(self.__header_line_items()))
        lines.append(separator.join(self.__data_items(statistics, matchup_count, variable_name, ref_variable_name)))

        if target_file is not None:
            self.__write_csv_to_file(target_file, lines)

        return '\n'.join(lines)

    def __write_header(self, lines):
        source = '' if self.source_file is None else ' of file \'{}\''.format(self.source_file)
        lines.append('##############################################################')
        lines.append('#')
        lines.append('# Benchmarking results' + source)
        lines.append('#')
        lines.append('##############################################################')
        lines.append('#')
        lines.append('# Created on {}'.format(datetime.now().strftime('%b %d, %Y at %H:%M:%S')))
        lines.append('#')
        lines.append('# Matchup criteria:')
        lines.append('#    Macro pixel size = {}'.format(self.config.macro_pixel_size))
        lines.append('#    Maximum geographic delta = {} \"degrees\"'.format(self.config.geo_delta))
        lines.append('#    Maximum time delta = {} seconds'.format(self.config.time_delta))
        # TODO - exclude depth if source file contains no depth dimension
        lines.append('#    Maximum depth delta = {} meters'.format(self.config.depth_delta))
        lines.append('#')
        lines.append('# Algorithm parameters:')
        lines.append('#    ddof (delta degrees of freedom, used for computation of stddev) = {}'.format(self.config.ddof))
        lines.append('#    alpha (used for percentile computation) = 1'.format(self.config.alpha))
        lines.append('#    beta (used for percentile computation) = 1'.format(self.config.beta))
        lines.append('#')

    def __rename(self, string):
        return str(string) if string is not None else 'Unknown'

    def __data_items(self, statistics, matchup_count, variable_name, ref_variable_name):
        matchup_count = self.__rename(matchup_count)
        variable_name = self.__rename(variable_name)
        ref_variable_name = self.__rename(ref_variable_name)
        data_items = [
            variable_name,
            ref_variable_name,
            matchup_count,
            str('%g' % round(statistics['min'], 4)),
            str('%g' % round(statistics['max'], 4)),
            str('%g' % round(statistics['mean'], 4)),
            str('%g' % round(statistics['stddev'], 4)),
            str('%g' % round(statistics['median'], 4)),
            str('%g' % round(statistics['p90'], 4)),
            str('%g' % round(statistics['p95'], 4)),
            str('%g' % round(statistics['ref_min'], 4)),
            str('%g' % round(statistics['ref_max'], 4)),
            str('%g' % round(statistics['ref_mean'], 4)),
            str('%g' % round(statistics['ref_stddev'], 4)),
            str('%g' % round(statistics['ref_median'], 4)),
            str('%g' % round(statistics['ref_p90'], 4)),
            str('%g' % round(statistics['ref_p95'], 4)),
            str('%g' % round(statistics['rmse'], 4)),
            str('%g' % round(statistics['unbiased_rmse'], 4)),
            str('%g' % round(statistics['bias'], 4)),
            str('%g' % round(statistics['pbias'], 4)),
            str('%g' % round(statistics['corrcoeff'], 4)),
            str('%g' % round(statistics['reliability_index'], 4)),
            str('%g' % round(statistics['model_efficiency'], 4))
        ]
        return data_items

    def __header_line_items(self):
        header_items = []
        basic_names = ['min', 'max', 'mean', 'stddev', 'median', 'p90', 'p95']
        header_items.append('variable_name')
        header_items.append('ref_variable_name')
        header_items.append('matchup_count')
        for bn in basic_names:
            header_items.append(bn)
        for bn in basic_names:
            header_items.append('ref_' + bn)
        header_items.append('rmse')
        header_items.append('unbiased_rmse')
        header_items.append('bias')
        header_items.append('pbias')
        header_items.append('corrcoeff')
        header_items.append('reliability_index')
        header_items.append('model_efficiency')
        return header_items

    def __write_csv_to_file(self, target_file, lines):
        directory = os.path.dirname(target_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = open(target_file, 'w')
        for line in lines:
            file.write("%s\n" % line)
        file.close()

    def taylor(self, target_file, statistics):
        diagram = Plotter.create_taylor_diagram(statistics, config=self.config)
        diagram.write(target_file)