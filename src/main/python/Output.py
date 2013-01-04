from datetime import datetime
import logging
from src.main.python import Processor
from src.main.python.Configuration import global_config
from src.main.python.MatchupEngine import MatchupEngine

class Output(object):

    def __init__(self, **kwargs):
        """Constructs a new instance of Output, tied to a set of statistics.
        Note that either a 'statistics' or a 'data' object needs to be passed.

        Keyword arguments:
            statistics -- the statistics to be output (mandatory if data is not given)
            data -- the data on which to compute statistics to be output (mandatory if statistics is not given)
            variable_name -- the model variable name (optional; mandatory if statistics is not given)
            ref_variable_name -- the reference variable name (optional; mandatory if statistics is not given)
            matchup_count -- the number of matchups (optional)
            source_file -- a reference to the file the benchmarks were computed on (optional)
        """

        self.variable_name = kwargs['variable_name'] if 'variable_name' in kwargs.keys() else None
        self.ref_variable_name = kwargs['ref_variable_name'] if 'ref_variable_name' in kwargs.keys() else None
        self.matchup_count = kwargs['matchup_count'] if 'matchup_count' in kwargs.keys() else None
        self.source_file = kwargs['source_file'] if 'source_file' in kwargs.keys() else None

        if 'statistics' not in kwargs and 'data' not in kwargs:
            raise ValueError('missing \'statistics\' or \'data\' argument')

        if 'statistics' in kwargs and 'data' in kwargs:
            logger = logging.getLogger('')
            logger.setLevel(logging.INFO)
            logger.warning('both \'statistics\' and \'data\' given: Ignoring \'data\'.')

        self.assign_statistics(kwargs)

    def assign_statistics(self, kwargs):
        if 'statistics' in kwargs.keys():
            self.statistics = kwargs['statistics']
        else:
            self.data = kwargs['data']
            if self.variable_name is None or self.ref_variable_name is None:
                raise ValueError("missing \'variable name\' and/or \'ref_variable_name\' argument(s)")
            config = global_config()
            me = MatchupEngine(self.data, config.macro_pixel_size, config.geo_delta, config.time_delta, config.depth_delta)
            matchups = me.find_all_matchups(self.ref_variable_name, self.variable_name)
            self.matchup_count = len(matchups)
            self.statistics = Processor.basic_statistics(matchups=matchups)

    def csv(self, include_header=True, separator='\t', target_file=None):
        """Outputs the statistics to CSV.

        Keyword arguments:
            include_header -- if meta information shall be included. Defaults to True
            separator -- the separator character used in the CSV output. Defaults to '\t'
            target_file -- if specified, the CSV will be written to the file. Defaults to None
        """

        lines = []
        if include_header:
            self.write_header(lines)
        lines.append(separator.join(self.header_line_items()))
        lines.append(separator.join(self.data_items()))

        if target_file is not None:
            self.write_to_file(target_file, lines)

        return '\n'.join(lines)

    def write_header(self, lines):
        config = global_config()
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
        lines.append('#    Macro pixel size = {}'.format(config.macro_pixel_size))
        lines.append('#    Maximum geographic delta = {} \"degrees\"'.format(config.geo_delta))
        lines.append('#    Maximum time delta = {} seconds'.format(config.time_delta))
        # TODO - exclude depth if source file contains no depth dimension
        lines.append('#    Maximum depth delta = {} meters'.format(config.depth_delta))
        lines.append('#')
        lines.append('# Parameters:')
        lines.append('#    ddof (delta degrees of freedom, used for computation of stddev) = {}'.format(config.ddof))
        lines.append('#    alpha (used for percentile computation) = 1'.format(config.alpha))
        lines.append('#    beta (used for percentile computation) = 1'.format(config.beta))
        lines.append('#')

    def rename(self, string):
        return str(string) if string is not None else 'Unknown'

    def data_items(self):
        matchup_count = self.rename(self.matchup_count)
        variable_name = self.rename(self.variable_name)
        ref_variable_name = self.rename(self.ref_variable_name)
        data_items = [
            variable_name,
            ref_variable_name,
            matchup_count,
            str('%g' % round(self.statistics['min'], 4)),
            str('%g' % round(self.statistics['max'], 4)),
            str('%g' % round(self.statistics['mean'], 4)),
            str('%g' % round(self.statistics['stddev'], 4)),
            str('%g' % round(self.statistics['median'], 4)),
            str('%g' % round(self.statistics['p90'], 4)),
            str('%g' % round(self.statistics['p95'], 4)),
            str('%g' % round(self.statistics['ref_min'], 4)),
            str('%g' % round(self.statistics['ref_max'], 4)),
            str('%g' % round(self.statistics['ref_mean'], 4)),
            str('%g' % round(self.statistics['ref_stddev'], 4)),
            str('%g' % round(self.statistics['ref_median'], 4)),
            str('%g' % round(self.statistics['ref_p90'], 4)),
            str('%g' % round(self.statistics['ref_p95'], 4)),
            str('%g' % round(self.statistics['rmsd'], 4)),
            str('%g' % round(self.statistics['unbiased_rmsd'], 4)),
            str('%g' % round(self.statistics['bias'], 4)),
            str('%g' % round(self.statistics['pbias'], 4)),
            str('%g' % round(self.statistics['corrcoeff'], 4)),
            str('%g' % round(self.statistics['reliability_index'], 4)),
            str('%g' % round(self.statistics['model_efficiency'], 4))
        ]
        return data_items

    def header_line_items(self):
        header_items = []
        basic_names = ['min', 'max', 'mean', 'stddev', 'median', 'p90', 'p95']
        header_items.append('variable_name')
        header_items.append('ref_variable_name')
        header_items.append('matchup_count')
        for bn in basic_names:
            header_items.append(bn)
        for bn in basic_names:
            header_items.append('ref_' + bn)
        header_items.append('rmsd')
        header_items.append('unbiased_rmsd')
        header_items.append('bias')
        header_items.append('pbias')
        header_items.append('corrcoeff')
        header_items.append('reliability_index')
        header_items.append('model_efficiency')
        return header_items

    def write_to_file(self, target_file, lines):
        file = open(target_file, 'w')
        for line in lines:
            file.write("%s\n" % line)
        file.close()