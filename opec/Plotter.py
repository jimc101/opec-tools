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

import logging
from math import copysign
import os

import matplotlib.pyplot as plt
import matplotlib.pylab as plb
from matplotlib import lines as mpl_lines
from matplotlib.patches import Ellipse
from matplotlib.projections.polar import PolarTransform
from mpl_toolkits.axisartist import SubplotZero
import numpy as np
import numpy.ma as ma
import mpl_toolkits.axisartist.floating_axes as FA
import mpl_toolkits.axisartist.grid_finder as GF
import matplotlib as mpl
import matplotlib.ticker
from matplotlib.cm import ScalarMappable as ScalarMappable
from opec import utils

from opec.configuration import get_default_config

if not os.name == 'nt':
    import resource

def create_taylor_diagrams(statistics, config=None):
    if config is None:
        config = get_default_config()

    statistics = utils.ensure_list(statistics)

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
                    continue

            figure = plt.figure()
            diagram = TaylorDiagram(figure, ref, config.show_negative_corrcoeff, config.show_legends, max_stddev)

            diagram.setup_axes()
            for stats in current_statistics:
                model_name = stats['model_name'] if 'model_name' in stats else None
                diagram.plot_sample(stats['corrcoeff'], stats['stddev'], model_name, stats['unit'])

            diagram.update_legend()
            diagrams.append(diagram)

    return diagrams

def create_target_diagram(statistics, config=None):
    figure = plt.figure()
    if config is None:
        config = get_default_config()

    statistics = utils.ensure_list(statistics)

    diagram = TargetDiagram(figure, config.normalise_target_diagram, config.show_legends, config.utilise_stddev_difference)

    diagram.setup_axes()
    for stats in statistics:
        diagram.plot_sample(stats['bias'], stats['unbiased_rmse'], stats['normalised_rmse'], stats['rmse'],
            stats['ref_stddev'], stats['stddev'], create_sample_name(stats['model_name'], stats['unit']))

    if config.normalise_target_diagram:
        diagram.plot_correcoeff_marker_line()

    diagram.update_legend()
    if not config.normalise_target_diagram:
        diagram.update_ranges(config.target_diagram_bounds)

    return diagram

def create_density_plot(ref_name, model_name, unit=None):
    figure = plt.figure()
    diagram = DensityPlot(figure, ref_name, model_name, unit)
    diagram.setup_axes()
    return diagram


class Diagram(object):

    def needs_update(self, value, field_name, func):
        if not hasattr(self, field_name):
            self.__setattr__(field_name, value)
        if value == func(value, self.__getattribute__(field_name)):
            self.__setattr__(field_name, value)
            return True
        return False

    def write(self, target_file):
        self.fig.savefig(target_file)

    def show(self):
        plt.show(self.fig)

    def get_figure(self):
        return self.fig

    def update_legend(self):
        if self.show_legend:
            self.fig.legend(self.sample_points, self.sample_names, numpoints=1, prop=dict(size='small'), loc='upper right')

    def get_color(self):
        if not hasattr(self, 'colors') or not self.colors:
            self.colors = ['r', 'g', 'b', 'm', 'y', 'c']
        return self.colors.pop(0)

class DensityPlot(Diagram):

    def __init__(self, figure, ref_name, model_name, unit=None):
        self.fig = figure
        self.x = []
        self.y = []
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


    def update_title(self, matchup_count):
        plt.title('Density plot of %s and %s\nNumber of considered matchups: %s' % (self.model_name, self.ref_name, matchup_count))


    def draw_regression_line(self, x_data, y_data):
        m, b = plb.polyfit(x_data.ravel(), y_data.ravel(), 1)
        x_lim = plt.xlim()
        data_y = [x_lim[0] * m + b, x_lim[1] * m + b]
        line = mpl_lines.Line2D(x_lim, data_y, color='blue', linewidth=0.4)
        plt.axes().add_line(line)


    def set_data(self, x_data, y_data, axis_min, axis_max, matchup_count, log):
        logging.debug('Creating density plot...')

        cmap = 'spectral_r'
        extent = [axis_min, axis_max, axis_min, axis_max]
        if log:
            bin_spec = 'log'
        else:
            bin_spec = None
        hexbin = self.ax.hexbin(x_data, y_data, bins=bin_spec, extent=extent, cmap=cmap)
        data = hexbin.get_array()

        mappable = ScalarMappable(cmap=cmap)
        mappable.set_array(data)
        self.fig.colorbar(mappable, ax=self.ax)

        logging.debug('...success!')
        self.update_title(matchup_count)


    def update_ranges(self, x_data, y_data):
        s_x = ma.mean(x_data)
        s_y = ma.mean(y_data)
        bounds = [ma.min(x_data) - s_x, ma.max(x_data) + s_x, ma.min(y_data) - s_y, ma.max(y_data) + s_y]
        plt.axis(bounds)


#noinspection PyUnusedLocal
def hide_zero(value, pos):
    if value == 0:
        return ''
    else:
        return value

#noinspection PyUnusedLocal
def move_zero(value, pos):
    if value == 0:
        return '       0.0'
    else:
        return value

class TargetDiagram(Diagram):
    """Target diagram: provides summary information about the pattern
    statistics as well as the bias thus yielding a broader overview of
    their respective contributions to the total RMSE (see Jolliff et al 2009 for details)."""

    def __init__(self, figure, normalise, show_legend, utilise_stddev_difference):
        self.fig = figure
        self.show_legend = show_legend
        self.normalise = normalise
        self.utilise_stddev_difference = utilise_stddev_difference
        self.x = []
        self.y = []

    def setup_axes(self):
        ax = self.fig.add_subplot(1, 1, 1)

        ax.spines['left'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_position('zero')
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())

        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(hide_zero))
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(move_zero))

        if self.normalise:
            ax.set_aspect('equal')
            plt.axis([-1.3, 1.3, -1.3, 1.3])
            marker_line = Ellipse((0,0), 2, 2, edgecolor='k', linewidth=0.8, fill=False)
            ax.add_artist(marker_line)
        self.ax = ax


    def plot_sample(self, bias, unbiased_rmse, normalised_rmse, rmse, ref_stddev, model_stddev, name):
        x = normalised_rmse if self.normalise else unbiased_rmse
        y = bias / ref_stddev if self.normalise else bias

        if self.utilise_stddev_difference:
            x = copysign(x, model_stddev - ref_stddev)

        self.x.append(x)
        self.y.append(y)

        data_value = self.ax.plot(x, y, '%sh' % self.get_color(), markersize=6)
        if hasattr(self, 'sample_names'):
            self.sample_points.append(data_value[0])
            self.sample_names.append(name)
        else:
            self.sample_points = [data_value[0]]
            self.sample_names = [name]

        if not hasattr(self, 'minimum_unbiased_rmse') or self.minimum_unbiased_rmse > rmse:
            self.minimum_unbiased_rmse = unbiased_rmse
            self.marker_radius = np.sqrt((bias / ref_stddev) ** 2 + normalised_rmse ** 2)

    def plot_correcoeff_marker_line(self):
        marker_line = Ellipse((0,0), 2 * self.marker_radius, 2 * self.marker_radius, edgecolor='k', linewidth=0.8, linestyle='dashed', fill=False)
        self.ax.add_artist(marker_line)

    def extract_bounds(self, target_rectangle):
        if target_rectangle is not None:
            min_x = target_rectangle[0]
            max_x = target_rectangle[1]
            min_y = target_rectangle[2]
            max_y = target_rectangle[3]
        else:
            min_x = None
            max_x = None
            min_y = None
            max_y = None
        return max_x, max_y, min_x, min_y

    def update_ranges(self, target_rectangle=None):
        max_x, max_y, min_x, min_y = self.extract_bounds(target_rectangle)
        max_x = max_x if max_x is not None else max(self.x)
        max_y = max_y if max_y is not None else max(self.y)
        min_x = min_x if min_x is not None else min(self.x)
        min_y = min_y if min_y is not None else min(self.y)
        growing_factor = 1.2
        max_x = growing_factor * max_x if max_x > 0 else max_x / growing_factor
        max_y = growing_factor * max_y if max_y > 0 else max_y / growing_factor
        min_x = growing_factor * min_x if min_x < 0 else min_x / growing_factor
        min_y = growing_factor * min_y if min_y < 0 else min_y / growing_factor
        plt.axis([min_x, max_x, min_y, max_y])


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
        for name, ref_stddev, unit in self.ref:
            dataset = self.ax.plot([0], ref_stddev, '%so' % self.get_color())[0]
            if hasattr(self, 'sample_names'):
                self.sample_points.append(dataset)
                self.sample_names.append(create_sample_name(name, unit))
            else:
                self.sample_points = [dataset]
                self.sample_names = [create_sample_name(name, unit)]

        # Add stddev contours
        t = np.linspace(0, x_max, num=50)
        for name, ref_stddev, unit in self.ref:
            if not np.isnan(ref_stddev):
                r = np.zeros_like(t) + ref_stddev # 50 times the stddev
                self.ax.plot(t, r, 'k--', label='_', linewidth=0.5)

        # Add rmse contours
        rs, ts = np.meshgrid(np.linspace(0, y_axis_range[1], num=50),
                             np.linspace(0, x_max, num=50))

        for name, ref_stddev, unit in self.ref:
            if not np.isnan(ref_stddev):
                # Unfortunately, I don't understand the next line AT ALL,
                # it's copied from http://matplotlib.1069221.n5.nabble.com/Taylor-diagram-2nd-take-td28070.html
                # but it leads to the right results (contours of the centered pattern RMS), so I keep it
                rmse = np.sqrt(ref_stddev ** 2 + rs ** 2 - 2 * ref_stddev * rs * np.cos(ts))

                colors = ('#7F0000', '#6F0000', '#5F0000', '#4F0000', '#3F0000', '#2F0000', '#1F0000', '#0F0000')
                rmse_contour = self.ax.contour(ts, rs, rmse, 8, linewidths=0.5, colors=colors)

                plt.clabel(rmse_contour, inline=1, fmt='%1.2f', fontsize=8)


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