from datetime import datetime
import os
from opec import Plotter
from opec.Configuration import get_default_config

def rename(string):
    return string if string is not None else 'Unknown'

def format_statistic(statistics, name):
    return '%g' % round(statistics[name], 4)

def key(string, is_ref_var):
    if is_ref_var:
        return 'ref_' + string
    return string

class Output(object):

    def __init__(self, **kwargs):
        """Constructs a new instance of Output.

        Keyword arguments:
            config -- the configuration the processors and matchup engine have been run with (optional)
            source_file -- a reference to the file the benchmarks were computed on (optional)
        """
        self.config = kwargs['config'] if 'config' in kwargs.keys() else get_default_config()
        self.source_file = kwargs['source_file'] if 'source_file' in kwargs.keys() else None
        self.separator = self.config.separator

    def csv(self, statistics, variable_name, ref_variable_name, matchups=None, target_file=None):
        """Outputs the statistics to CSV.

        Arguments:
            variable_name -- the model variable name
            ref_variable_name -- the reference variable name
            matchups -- the matchups used to calculate the statistics (optional)
            target_file -- if specified, the CSV will be written to the file. (optional)
        """

        if variable_name is None:
            raise ValueError('Missing parameter \'variable_name\'')
        if ref_variable_name is None:
            raise ValueError('Missing parameter \'ref_variable_name\'')

        include_header = self.config.include_header

        lines = []
        if include_header:
            self.__write_header(lines, matchups)
        lines.append('\n'.join(self.__reference_statistics(statistics, variable_name, ref_variable_name)))
        lines.append('')
        lines.append('\n'.join(self.__single_statistics(statistics, variable_name, False)))
        lines.append('')
        lines.append('\n'.join(self.__single_statistics(statistics, ref_variable_name, True)))
        if matchups is not None:
            lines.append('')
            lines.append('# Matchups:')
            lines.append('')
            for matchup_number, matchup in enumerate(matchups):
                lines.append('\n'.join(self.__matchup_infos(matchup_number, matchup)))

        if target_file is not None:
            self.__write_csv_to_file(target_file, lines)

        return '\n'.join(lines)

    def __write_header(self, lines, matchups):
        source = '' if self.source_file is None else ' of file \'{}\''.format(self.source_file)
        lines.append('##############################################################')
        lines.append('#')
        lines.append('# Benchmarking results' + source)
        lines.append('#')
        lines.append('##############################################################')
        lines.append('#')
        lines.append('# Created on {}'.format(datetime.now().strftime('%b %d, %Y at %H:%M:%S')))
        lines.append('#')
        if matchups is not None:
            lines.append('# Number of matchups: %s' % len(matchups))
        lines.append('#')
        lines.append('# Matchup criteria:')
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

    def __reference_statistics(self, stats, model_variable, reference_variable):
        lines = []
        lines.append('# Statistics for variable \'%s\' with reference \'%s\':' % (model_variable, reference_variable))
        lines.append('')
        lines.append('rmse%s%s' % (self.separator, format_statistic(stats, 'rmse')))
        lines.append('unbiased_rmse%s%s' % (self.separator, format_statistic(stats, 'unbiased_rmse')))
        lines.append('bias%s%s' % (self.separator, format_statistic(stats, 'bias')))
        lines.append('pbias%s%s' % (self.separator, format_statistic(stats, 'pbias')))
        lines.append('corrcoeff%s%s' % (self.separator, format_statistic(stats, 'corrcoeff')))
        lines.append('reliability_index%s%s' % (self.separator, format_statistic(stats, 'reliability_index')))
        lines.append('model_efficiency%s%s' % (self.separator, format_statistic(stats, 'model_efficiency')))
        return lines

    def __single_statistics(self, stats, variable, is_ref_var):
        lines = []
        lines.append('# Statistics of variable \'%s\':' % variable)
        lines.append('')
        lines.append('min%s%s' % (self.separator, format_statistic(stats, key('min', is_ref_var))))
        lines.append('max%s%s' % (self.separator, format_statistic(stats, key('max', is_ref_var))))
        lines.append('mean%s%s' % (self.separator, format_statistic(stats, key('mean', is_ref_var))))
        lines.append('stddev%s%s' % (self.separator, format_statistic(stats, key('stddev', is_ref_var))))
        lines.append('median%s%s' % (self.separator, format_statistic(stats, key('median', is_ref_var))))
        lines.append('p90%s%s' % (self.separator, format_statistic(stats, key('p90', is_ref_var))))
        lines.append('p95%s%s' % (self.separator, format_statistic(stats,key('p95', is_ref_var))))
        return lines

    def __matchup_infos(self, matchup_number, matchup):
        lines = []
        lines.append('# Matchup %s:' % (matchup_number + 1))
        lines.append('')
        lines.append('reference_time:%s%s' % (self.separator, matchup.reference_record.time))
        lines.append('reference_depth:%s%s' % (self.separator, matchup.reference_record.depth))
        lines.append('reference_lat:%s%s' % (self.separator, matchup.reference_record.lat))
        lines.append('reference_lon:%s%s' % (self.separator, matchup.reference_record.lon))
        lines.append('model_time:%s%s' % (self.separator, matchup.spacetime_position[0]))
        lines.append('model_depth:%s%s' % (self.separator, matchup.spacetime_position[1]))
        lines.append('model_lat:%s%s' % (self.separator, matchup.spacetime_position[2]))
        lines.append('model_lon:%s%s' % (self.separator, matchup.spacetime_position[3]))
        return lines

    def __write_csv_to_file(self, target_file, lines):
        directory = os.path.dirname(target_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = open(target_file, 'w')
        for line in lines:
            file.write("%s\n" % line)
        file.close()

    def taylor(self, statistics, target_file):
        diagram = Plotter.create_taylor_diagram(statistics, config=self.config)
        diagram.write(target_file)