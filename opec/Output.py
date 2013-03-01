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

import numpy as np
from io import StringIO
from mako.runtime import Context
from mako.template import Template
from datetime import datetime
import os
from opec import Plotter
from opec.Configuration import get_default_config

def rename(string):
    return string if string is not None else 'Unknown'


def format_statistic(statistics, name):
    value = statistics[name]
    if value is np.ma.masked or np.isneginf(value) or np.isnan(value):
        return 'nan'
    return '%g' % round(value, 4)


def key(string, is_ref_var):
    if is_ref_var:
        return 'ref_' + string
    return string

def get_basenames(files):
    basenames = []
    if files is not None:
        for file in files:
            basenames.append(os.path.basename(file))
    return basenames

class Output(object):
    def __init__(self, data, **kwargs):
        """Constructs a new instance of Output.

        Keyword arguments:
            config -- the configuration the processors and matchup engine have been run with (optional)
            source_file -- a reference to the file the benchmarks were computed on (optional)
        """
        self.config = kwargs['config'] if 'config' in kwargs.keys() and kwargs[
                                                                        'config'] is not None else get_default_config()
        self.source_file = kwargs['source_file'] if 'source_file' in kwargs.keys() else None
        self.separator = self.config.separator
        self.data = data

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
            matchup_lines = self.__matchup_infos(matchups)

        if matchups is not None and not self.config.separate_matchups:
            lines.append('')
            #noinspection PyUnboundLocalVariable
            lines.extend(matchup_lines)

        if target_file is not None:
            self.__write_lines_to_file(target_file, lines)
            if matchups is not None and self.config.separate_matchups:
                matchup_filename = '%s_matchups.csv' % os.path.splitext(target_file)[0]
                self.__write_lines_to_file(matchup_filename, matchup_lines)

        return '\n'.join(lines)

    def __write_header(self, lines, matchups):
        source = '' if self.source_file is None else ' of file \'{}\''.format(self.source_file)
        lines.append('##############################################################')
        lines.append('#')
        lines.append('# Benchmarking results' + source)
        lines.append('#')
        lines.append('##############################################################')
        lines.append('#')
        lines.append('# Performed at {}'.format(datetime.now().strftime('%b %d, %Y at %H:%M:%S')))
        lines.append('#')
        if matchups is not None:
            lines.append('# Number of matchups: %s' % len(matchups))
        lines.append('#')
        lines.append('# Matchup criteria:')
        lines.append('#    Maximum time delta = {} seconds'.format(self.config.time_delta))
        lines.append('#    Maximum depth delta = {} meters'.format(self.config.depth_delta))
        lines.append('#')
        lines.append('# Algorithm parameters:')
        lines.append(
            '#    ddof (delta degrees of freedom, used for computation of stddev) = {}'.format(self.config.ddof))
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
        lines.append('p95%s%s' % (self.separator, format_statistic(stats, key('p95', is_ref_var))))
        return lines

    def __matchup_infos(self, matchups):
        header = []
        header.append('Matchup #')
        header.append('reference_time')
        header.append('reference_depth')
        header.append('reference_lat')
        header.append('reference_lon')
        header.append('model_time')
        header.append('model_depth')
        header.append('model_lat')
        header.append('model_lon')
        ref_vars = self.data.ref_vars()
        model_vars = self.data.model_vars()
        header.extend(ref_vars)
        header.extend(model_vars)
        # for matchup in matchups:
        #     for var in matchup.values:
        #         if not var in header:
        #             header.append(var)
        #             vars.append(var)

        lines = [self.config.separator.join(header)]
        for matchup in matchups:
            line = []
            line.append(str(matchup.reference_record.record_number))
            line.append(str(matchup.reference_record.time))
            line.append(str(matchup.reference_record.depth))
            line.append(str(matchup.reference_record.lat))
            line.append(str(matchup.reference_record.lon))
            line.append(str(matchup.spacetime_position[0]))
            line.append(str(matchup.spacetime_position[1]))
            line.append(str(matchup.spacetime_position[2]))
            line.append(str(matchup.spacetime_position[3]))
            for var in ref_vars:
                line.append(str(matchup.get_ref_value(var, self.data)))
            for var in model_vars:
                line.append(str(matchup.get_model_value(var, self.data)))
            lines.append(self.config.separator.join(line))
        return lines

    def __write_lines_to_file(self, target_file, lines):
        directory = os.path.dirname(target_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = open(target_file, 'w')
        for line in lines:
            file.write("%s\n" % line)
        file.close()

    def xhtml(self, statistics_list, matchups, data, target_file, taylor_target_files=None, target_diagram_file=None, scatter_plot_files=None):
        filename = os.path.dirname(os.path.realpath(__file__)) + '/../resources/matchup_report_template.xml'
        template = Template(filename=filename)
        buf = StringIO()

        all_relative_stats = []
        all_model_stats = []
        all_ref_stats = []
        for stats in statistics_list:
            pair_statistics = {}
            for key in ('rmse', 'unbiased_rmse', 'bias', 'pbias', 'corrcoeff', 'reliability_index', 'model_efficiency'):
                pair_statistics[key] = format_statistic(stats, key)
            pair = (stats['model_name'], stats['ref_name'], pair_statistics)
            all_relative_stats.append(pair)

            model_pair = {}
            for key in ('min', 'max', 'mean', 'stddev', 'median', 'p90', 'p95'):
                model_pair[key] = format_statistic(stats, key)
            all_model_stats.append((stats['model_name'], model_pair))

            ref_pair = {}
            for key in ('ref_min', 'ref_max', 'ref_mean', 'ref_stddev', 'ref_median', 'ref_p90', 'ref_p95'):
                ref_pair[key.replace('ref_', '')] = format_statistic(stats, key)
            all_ref_stats.append((stats['ref_name'], ref_pair))

        scatter_plot_files = get_basenames(scatter_plot_files)
        taylor_target_files = get_basenames(taylor_target_files)
        target_diagram_file = os.path.basename(target_diagram_file) if target_diagram_file is not None else None

        ctx = Context(buf,
            pairs=all_relative_stats,
            performed_at=datetime.now().strftime('%b %d, %Y at %H:%M:%S'),
            record_count=len(matchups),
            time_delta=self.config.time_delta,
            depth_delta=self.config.depth_delta,
            ddof=self.config.ddof,
            alpha=self.config.alpha,
            beta=self.config.beta,
            all_relative_stats=all_relative_stats,
            all_model_stats=all_model_stats,
            all_ref_stats=all_ref_stats,
            matchups=matchups,
            data=data,
            reference_vars=data.ref_vars(),
            model_vars=data.model_vars(),
            write_taylor_diagrams=self.config.write_taylor_diagrams,
            taylor_target_files=taylor_target_files,
            write_target_diagram=self.config.write_target_diagram,
            target_diagram_file=target_diagram_file,
            scatter_plot_files=scatter_plot_files)
        template.render_context(ctx)
        xml = buf.getvalue()

        directory = os.path.dirname(target_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = open(target_file, 'w')
        file.write(xml)
        file.close()

    def taylor(self, statistics, target_file=None):
        diagrams = Plotter.create_taylor_diagrams(statistics, config=self.config)
        result = []
        if target_file is not None:
            for i, diagram in enumerate(diagrams):
                last_index_of_dot = target_file.rfind('.')
                new_target_file = target_file[:last_index_of_dot] + '_' + str(i) + target_file[last_index_of_dot:]
                diagram.write(new_target_file)
                result.append(new_target_file)
        return result, diagrams

    def scatter_plot(self, matchups, data, ref_name, model_name, target_file=None, unit=None):
        diagram = Plotter.create_scatter_plot(matchups, data, ref_name, model_name, unit)
        if target_file is not None:
            diagram.write(target_file)
        return diagram

    def target_diagram(self, statistics, target_file=None):
        target_diagram = Plotter.create_target_diagram(statistics, self.config)
        if target_file is not None:
            target_diagram.write(target_file)
        return target_diagram