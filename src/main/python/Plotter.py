from matplotlib import pyplot
from matplotlib.projections.polar import PolarTransform
import numpy as np
import mpl_toolkits.axisartist.floating_axes as FA
import mpl_toolkits.axisartist.grid_finder as GF

def create_taylor_diagram(ref_stddev, statistics, target_file=None):
    diagram = TaylorDiagram(ref_stddev)
    figure = pyplot.figure()

    diagram.setup_axes(figure)
    for stats in statistics:
        diagram.plot_sample(stats['corrcoeff'], stats['stddev'], 'yh')

    if target_file is not None:
        pyplot.savefig(target_file)

    return diagram

def create_target_diagram():
    pass

class TaylorDiagram(object):
    """Taylor diagram: plot model standard deviation and correlation
    to reference (data) sample in a single-quadrant polar plot, with
    r=stddev and theta=arccos(correlation).

    Developed on basis of implementation at:
    http://matplotlib.1069221.n5.nabble.com/Taylor-diagram-2nd-take-td28070.html
    """

    def __init__(self, ref_stddev, show_negative_corrcoeff=True):
        self.ref_stddev = ref_stddev
        self.show_negative_corrcoeff = show_negative_corrcoeff

    def setup_axes(self, fig):
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

        y_max = 1.5 * self.ref_stddev # the stddev-axis shall go from 0 to 1.5-times of the stddev
        x_max = np.pi if self.show_negative_corrcoeff else np.pi / 2
        ghelper = FA.GridHelperCurveLinear(tr,
            extremes=(
                0, x_max, # show in grid only the 1st quadrant: from 0 degrees to pi/2 degrees
                0, y_max),
            grid_locator1=gl1,
            tick_formatter1=tf1,
        )

        ax = FA.FloatingSubplot(fig, 111, grid_helper=ghelper) # 111 -> plot contains 1 row, 1 col and shall be located at position 1 (1-based!) in the resulting grid
        fig.add_subplot(ax)
        if self.show_negative_corrcoeff:
            fig.text(0.41, 0.178, 'Standard Deviation') # magic numbers: place label central below plot

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

        # Add reference point

        # [0] = x-value
        # self.modelData.std() = y-value
        # 'bo' = blue circle
        self.ax.plot([0], self.ref_stddev, 'b*')

        # Add stddev contour
        t = np.linspace(0, x_max, num=50) # 50 values linearly distributed between 0 and pi/2
        r = np.zeros_like(t) + self.ref_stddev # 50 times the stddev
        self.ax.plot(t, r, 'k--', label='_', linewidth=0.5)

        # Add rmse contour
        rs, ts = np.meshgrid(np.linspace(0, y_max, num=50),
            np.linspace(0, x_max, num=50))

        # Unfortunately, I don't understand the next line AT ALL,
        # it's copied from http://matplotlib.1069221.n5.nabble.com/Taylor-diagram-2nd-take-td28070.html
        # but it leads to the right results (contours of the centered pattern RMS), so I keep it
        rmse = np.sqrt(self.ref_stddev ** 2 + rs ** 2 - 2 * self.ref_stddev * rs * np.cos(ts))

        colors = ('#7F0000', '#6F0000', '#5F0000', '#4F0000', '#3F0000', '#2F0000', '#1F0000', '#0F0000')
        rmse_contour = self.ax.contour(ts, rs, rmse, 8, linewidths=0.5, colors=colors)

        pyplot.clabel(rmse_contour, inline=1, fmt='%1.2f', fontsize=8)

        return self.ax

    def get_angle(self, corrcoeff):
        return np.arccos(corrcoeff)

    def plot_sample(self, corrcoeff, model_stddev, *args, **kwargs):
        """Add model sample to the Taylor diagram. args and kwargs are
        directly propagated to the plot command."""

        theta = self.get_angle(corrcoeff)
        radius = model_stddev
        self.ax.plot(theta, radius, *args, **kwargs)

