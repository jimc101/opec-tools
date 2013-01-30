import logging
from matplotlib import pyplot, pylab
from matplotlib.projections.polar import PolarTransform
from mpl_toolkits.axisartist import SubplotZero
import numpy as np
import mpl_toolkits.axisartist.floating_axes as FA
import mpl_toolkits.axisartist.grid_finder as GF
from opec.Configuration import get_default_config
import matplotlib as mpl
import matplotlib.ticker

def add_statistics_by_unit(unit, stx, statistics_dict):
    if not unit in statistics_dict:
        statistics_dict[unit] = []
    statistics_dict[unit].append(stx)


def add_statistics_by_name_and_unit(current_name, current_unit, statistics, statistics_dict):
    if not current_name in statistics_dict.keys():
        statistics_dict[current_name] = {}
    if not current_unit in statistics_dict[current_name].keys():
        statistics_dict[current_name][current_unit] = []
    statistics_dict[current_name][current_unit].append(statistics)


def sort_statistics_by_name_and_unit(config, statistics):
    statistics_by_unit = {}
    for stx in statistics:
        if config.split_on_unit:
            unit_name = stx['unit']
        else:
            unit_name = 'dummy_unit'
        add_statistics_by_unit(unit_name, stx, statistics_by_unit)

    statistics_by_name_and_unit = {}
    for current_unit in statistics_by_unit.keys():
        if config.split_on_name:
            for current_stx in statistics_by_unit[current_unit]:
                current_name = current_stx['model_name']
                add_statistics_by_name_and_unit(current_name, current_unit, current_stx, statistics_by_name_and_unit)
        else:
            for current_stx in statistics_by_unit[current_unit]:
                add_statistics_by_name_and_unit('dummy_name', current_unit, current_stx, statistics_by_name_and_unit)
    return statistics_by_name_and_unit


def create_taylor_diagrams(statistics, config=None):
    if config is None:
        config = get_default_config()

    statistics_by_name_and_unit = sort_statistics_by_name_and_unit(config, statistics)
    diagrams = []

    for name in statistics_by_name_and_unit.keys():
        for current_unit in statistics_by_name_and_unit[name].keys():
            current_statistics = statistics_by_name_and_unit[name][current_unit]

            ref_stddevs = list(map(lambda x: x.get('ref_stddev'), current_statistics))
            ref_names = list(map(lambda x: x.get('ref_name'), current_statistics))
            units = list(map(lambda x: x.get('unit'), current_statistics))
            ref = tuple(zip(ref_names, ref_stddevs, units))
            max_stddev = max(ref_stddevs) * 1.5

            for v in ref_stddevs:
                if v == 0.0 or np.isnan(v):
                    logging.warning('Unable to create Taylor diagram from statistics.')
                    logging.debug('Statistics: %s' % current_statistics)
                    return None

            figure = pyplot.figure()
            diagram = TaylorDiagram(figure, ref, config.show_negative_corrcoeff, config.show_legend, max_stddev)

            diagram.setup_axes()
            for stats in current_statistics:
                model_name = stats['model_name'] if 'model_name' in stats else None
                diagram.plot_sample(stats['corrcoeff'], stats['stddev'], model_name, stats['unit'])

            diagrams.append(diagram)

    return diagrams

def create_target_diagram(statistics, config=None):
    figure = pyplot.figure()
    diagram = TargetDiagram(figure)

    diagram.setup_axes()
    for stats in statistics:
#        diagram.plot_sample(stats['bias'], stats['unbiased_rmse'], stats['rmse'])
        pass

    return diagram

def create_scatter_plot(reference_values, model_values, ref_name, model_name, unit=None):
    figure = pyplot.figure()
    diagram = ScatterPlot(figure, ref_name, model_name, unit)
    diagram.setup_axes()
    for (ref_value, model_value) in zip(reference_values, model_values):
        diagram.plot_sample(ref_value, model_value)
    return diagram

class Diagram(object):

    def write(self, target_file):
        self.fig.savefig(target_file)

class ScatterPlot(Diagram):

    def __init__(self, figure, ref_name, model_name, unit=None):
        self.fig = figure
        self.x = np.array([])
        self.y = np.array([])
        self.model_name = model_name
        self.ref_name = ref_name
        self.unit_string = '(%s)' % unit if unit is not None else ''

    def setup_axes(self):
        ax = SubplotZero(self.fig, 1, 1, 1)
        self.fig.add_subplot(ax)
        ax.set_xlabel('%s %s' % (self.ref_name, self.unit_string))
        ax.set_ylabel('%s %s' % (self.model_name, self.unit_string))
        ax.grid()
        self.ax = ax
        self.update_title()
        return ax

    def update_title(self):
        matchup_count = len(self.ax.lines)
        self.ax.set_title('Scatter plot of %s and %s\nNumber of considered matchups: %s' % (self.model_name, self.ref_name, matchup_count))

    def needs_update(self, value, field_name, func):
        if not hasattr(self, field_name):
            self.__setattr__(field_name, value)
        if value == func(value, self.__getattribute__(field_name)):
            self.__setattr__(field_name, value)
            return True
        return False

    def plot_sample(self, ref_value, model_value):
        if np.ma.masked in [ref_value, model_value]:
            return
        update_ranges = self.needs_update(ref_value, 'xmin', min)
        update_ranges |= self.needs_update(model_value, 'ymin', min)
        update_ranges |= self.needs_update(ref_value, 'xmax', max)
        update_ranges |= self.needs_update(model_value, 'ymax', max)
        xmin, xmax = 0, 0
        if update_ranges:
            xmin = self.__getattribute__('xmin')
            growing_factor = 1.2
            xmin = xmin * growing_factor if xmin < 0 else xmin / growing_factor
            ymin = self.__getattribute__('ymin')
            ymin = ymin * growing_factor if ymin < 0 else ymin / growing_factor
            xmax = self.__getattribute__('xmax')
            xmax = xmax * growing_factor if xmax > 0 else xmax / growing_factor
            ymax = self.__getattribute__('ymax')
            ymax = ymax * growing_factor if ymax > 0 else ymax / growing_factor
            pyplot.axis([xmin, xmax, ymin, ymax])

        self.x = np.append(self.x, ref_value)
        self.y = np.append(self.y, model_value)
        m, b = pylab.polyfit(self.x, self.y, 1)

        line, = pyplot.plot([xmin, xmax], [m * xmin + b, m * xmax + b], '-b', linewidth=0.4)
        if hasattr(self, 'line'):
            self.ax.lines.remove(self.line)
        self.line = line

        self.update_title()

        pyplot.plot(ref_value, model_value, 'ro', markersize=4)

class TargetDiagram(Diagram):
    """Target diagram: provides summary information about the pattern
    statistics as well as the bias thus yielding a broader overview of
    their respective contributions to the total RMSE (see Jolliff et al 2009 for details)."""

    def __init__(self, figure):
        self.fig = figure

    def setup_axes(self):
        ax = SubplotZero(self.fig, 111)
        self.fig.add_subplot(ax)

        for direction in ["xzero", "yzero"]:
            ax.axis[direction].set_axisline_style("-|>")
            ax.axis[direction].set_visible(True)

        for direction in ["left", "right", "bottom", "top"]:
            ax.axis[direction].set_visible(False)

        pylab.xlim(-1.0, 1.0)
        pylab.ylim(-1.0, 1.0)

        return ax

class TaylorDiagram(Diagram):
    """Taylor diagram: plot model standard deviation and correlation
    to reference (data) sample in a single-quadrant polar plot, with
    r=stddev and theta=arccos(correlation).

    Developed on basis of implementation at:
    http://matplotlib.1069221.n5.nabble.com/Taylor-diagram-2nd-take-td28070.html
    """

    def __init__(self, figure, ref, show_negative_corrcoeff, show_legend, max_stddev):
        self.fig = figure
        self.show_negative_corrcoeff = show_negative_corrcoeff
        self.show_legend = show_legend
        self.max_stddev = max_stddev
        self.ref = ref

    def get_color(self):
        if not hasattr(self, 'colors') or not self.colors:
            self.colors = ['r', 'g', 'b', 'm', 'y', 'c']
        return self.colors.pop(0)

    def setup_axes(self):
        """Set up Taylor diagram axes, i.e. single quadrant polar
        plot, using mpl_toolkits.axisartist.floating_axes.
        """

        tr = PolarTransform()

        # Intervals on the axis of the correlation coefficient
        rlocs = np.concatenate(([-1.0, -0.99, -0.95], np.arange(-10, 0) / 10.0, np.arange(10) / 10.0, [0.95, 0.99]))

        # The same intervals as angles
        tlocs = np.arccos(rlocs) # Conversion to polar angles

        gl1 = GF.FixedLocator(tlocs)    # Positions
        tf1 = GF.DictFormatter(dict(zip(tlocs, map(str, rlocs)))) # maps coefficient angles to string representation of correlation coefficient

        x_max = np.pi if self.show_negative_corrcoeff else np.pi / 2
        x_axis_range = (0, x_max)
        y_axis_range = (0, self.max_stddev)
        ghelper = FA.GridHelperCurveLinear(tr,
            extremes=(
                x_axis_range[0], x_axis_range[1],
                y_axis_range[0], y_axis_range[1]),
            grid_locator1=gl1,
            tick_formatter1=tf1,
        )

        ax = FA.FloatingSubplot(self.fig, 111, grid_helper=ghelper) # 111 -> plot contains 1 row, 1 col and shall be located at position 1 (1-based!) in the resulting grid
        self.fig.add_subplot(ax)
        if self.show_negative_corrcoeff:
            self.fig.text(0.41, 0.178, 'Standard Deviation') # magic numbers: place label central below plot

        # Setup axes
        ax.axis["top"].set_axis_direction("bottom")  # "Angle axis"
        ax.axis["top"].toggle(ticklabels=True, label=True)
        ax.axis["top"].major_ticklabels.set_axis_direction("top")
        ax.axis["top"].label.set_axis_direction("top")
        ax.axis["top"].label.set_text("Correlation coefficient")

        if not self.show_negative_corrcoeff:
            ax.axis["left"].set_axis_direction("bottom") # "X axis"
            ax.axis["left"].label.set_text("Standard deviation")
        else:
            ax.axis["left"].set_axis_direction("bottom") # "X axis"

        ax.axis["right"].set_axis_direction("top")   # "Y axis"
        ax.axis["right"].toggle(ticklabels=True, label=True)
        tick_axis_direction = "bottom" if self.show_negative_corrcoeff else "left"
        ax.axis["right"].major_ticklabels.set_axis_direction(tick_axis_direction)
        label_axis_direction = "bottom" if self.show_negative_corrcoeff else "left"
        ax.axis["right"].label.set_axis_direction(label_axis_direction)
        if not self.show_negative_corrcoeff:
            ax.axis["right"].label.set_text("Standard deviation")

        ax.axis["bottom"].set_visible(False)         # Hide useless axis

        # Grid
        ax.grid()

        # This defines how to draw the data -- putting the polar transform here forces the plot to draw the data on
        # the polar plot instead of a rectangular one
        self.ax = ax.get_aux_axes(tr)

        # Add reference points
        # [0] = x-value
        # stddev = y-value
        for name, stddev, unit in self.ref:
            dataset = self.ax.plot([0], stddev, '%so' % self.get_color())[0]
            if hasattr(self, 'sample_names'):
                self.sample_points.append(dataset)
                self.sample_names.append(create_sample_name(name, unit))
            else:
                self.sample_points = [dataset]
                self.sample_names = [create_sample_name(name, unit)]

        # Add stddev contours
        t = np.linspace(0, x_max, num=50)
        for name, ref_stddev, unit in self.ref:
            r = np.zeros_like(t) + ref_stddev # 50 times the stddev
            self.ax.plot(t, r, 'k--', label='_', linewidth=0.5)

        # Add rmse contours
        rs, ts = np.meshgrid(np.linspace(0, y_axis_range[1], num=50),
            np.linspace(0, x_max, num=50))

        for name, ref_stddev, unit in self.ref:
            # Unfortunately, I don't understand the next line AT ALL,
            # it's copied from http://matplotlib.1069221.n5.nabble.com/Taylor-diagram-2nd-take-td28070.html
            # but it leads to the right results (contours of the centered pattern RMS), so I keep it
            rmse = np.sqrt(ref_stddev ** 2 + rs ** 2 - 2 * ref_stddev * rs * np.cos(ts))

            colors = ('#7F0000', '#6F0000', '#5F0000', '#4F0000', '#3F0000', '#2F0000', '#1F0000', '#0F0000')
            rmse_contour = self.ax.contour(ts, rs, rmse, 8, linewidths=0.5, colors=colors)

            pyplot.clabel(rmse_contour, inline=1, fmt='%1.2f', fontsize=8)

        return self.ax

    def get_angle(self, corrcoeff):
        return np.arccos(corrcoeff)

    def plot_sample(self, corrcoeff, model_stddev, model_name=None, unit=None, *args, **kwargs):
        """Add model sample to the Taylor diagram. args and kwargs are
        directly propagated to the plot command."""

        if not args:
            args = ['%sh' % self.get_color()]

        theta = self.get_angle(corrcoeff)
        radius = model_stddev
        v = self.ax.plot(theta, radius, *args, **kwargs)
        self.sample_points.append(v[0])
        sample_name = create_sample_name(model_name, unit)
        self.sample_names.append(sample_name)
        self.update_legend()

    def update_legend(self):
        if self.show_legend:
            self.fig.legend(self.sample_points, self.sample_names, numpoints=1, prop=dict(size='small'), loc='upper right')

class CenteredFormatter(mpl.ticker.ScalarFormatter):
    """Acts exactly like the default Scalar Formatter, but yields an empty
    label for ticks at "center"."""
    center = 0
    def __call__(self, value, pos=None):
        if value == self.center:
            return ''
        else:
            return mpl.ticker.ScalarFormatter.__call__(self, value, pos)

def create_sample_name(model_name, unit):
    if model_name is not None:
        sample_name = model_name
    else:
        sample_name = 'Model value'
    if unit is not None:
        sample_name = sample_name + ' (%s)' % unit
    return sample_name