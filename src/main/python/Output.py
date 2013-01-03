from datetime import datetime

class Output(object):

    def __init__(self, configuration=None):
        if configuration is not None:
            self.configuration = configuration

    # todo: use **kwargs instead of 10000 parameters
    def output_basic_statistics(self, variable_name=None, ref_variable_name=None, matchup_count=None, basic_statistics=None, target=None, include_header=None, macro_pixel_size=None, geo_delta=None, time_delta=None, depth_delta=None, source_file=None, separator='\t'):
        if include_header:
            self.write_header(target, macro_pixel_size, geo_delta, time_delta, depth_delta, source_file)
        target.write_line(separator.join(header_line_items()))
        target.write_line(separator.join(data_items(variable_name, ref_variable_name, matchup_count, basic_statistics)))

    def write_header(self, target, macro_pixel_size, geo_delta, time_delta, depth_delta, source_file):
        source = '' if source_file is None else ' of file \'{}\''.format(source_file)
        now = datetime.now()
        target.write_line('##############################################################')
        target.write_line('#')
        target.write_line('# Benchmarking results' + source)
        target.write_line('#')
        target.write_line('##############################################################')
        target.write_line('#')
        target.write_line("# Created on {} {}, {} at {}:{}:{}".format(now.month, now.day, now.year, now.hour, now.minute, now.second))
        target.write_line("#")
        target.write_line("# Matchup criteria:")
        target.write_line("#    Macro pixel size = {}".format(macro_pixel_size))
        target.write_line("#    Maximum geographic delta = {} \"degrees\"".format(geo_delta))
        target.write_line("#    Maximum time delta = {} seconds".format(time_delta))
        if depth_delta is not None:
            target.write_line("#    Maximum depth delta = {} meters".format(depth_delta))
        target.write_line("#")

def header_line_items():
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


def data_items(variable_name, ref_variable_name, matchup_count, basic_statistics):
    data_items = [
        variable_name,
        ref_variable_name,
        str(matchup_count),
        str(basic_statistics['min']),
        str(basic_statistics['max']),
        str(basic_statistics['mean']),
        str(basic_statistics['stddev']),
        str(basic_statistics['median']),
        str(basic_statistics['p90']),
        str(basic_statistics['p95']),
        str(basic_statistics['ref_min']),
        str(basic_statistics['ref_max']),
        str(basic_statistics['ref_mean']),
        str(basic_statistics['ref_stddev']),
        str(basic_statistics['ref_median']),
        str(basic_statistics['ref_p90']),
        str(basic_statistics['ref_p95']),
        str(basic_statistics['rmsd']),
        str(basic_statistics['unbiased_rmsd']),
        str(basic_statistics['bias']),
        str(basic_statistics['pbias']),
        str(basic_statistics['corrcoeff']),
        str(basic_statistics['reliability_index']),
        str(basic_statistics['model_efficiency'])
        ]
    return data_items

class StringOutputter(object):

    def __init__(self):
        self.strings = []

    def write_line(self, line):
        self.strings.append(line)

    def finish(self):
        return '\n'.join(self.strings)