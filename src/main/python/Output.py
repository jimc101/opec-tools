from datetime import datetime

class Output(object):

    def __init__(self, configuration=None):
        if configuration is not None:
            self.configuration = configuration

    # todo: use **kwargs instead of 10000 parameters
    def output_basic_statistics(self, basic_statistics=None, matchups=None, target=None, include_header=None, macro_pixel_size=None, separator=None):
        if include_header:
            self.write_header(target)

    def write_header(self, target):
        now = datetime.now()
        target.write_line('##############################################################')
        target.write_line('#')
        target.write_line('# Benchmarking results')
        target.write_line('#')
        target.write_line('##############################################################')
        target.write_line('#')
        target.write_line("# Created on {} {}, {} at {}:{}:{}".format(now.month, now.day, now.year, now.hour, now.minute, now.second))
        target.write_line("#")
        target.write_line("# Matchup criteria:")


class StringOutputter(object):

    def __init__(self):
        self.strings = []

    def write_line(self, line):
        self.strings.append(line)

    def close(self):
        return '\n'.join(self.strings)