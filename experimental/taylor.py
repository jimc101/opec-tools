from matplotlib import pyplot
import numpy

class TaylorDiagram(object):
    """Taylor diagram: plot model standard deviation and correlation
    to reference (data) sample in a single-quadrant polar plot, with
    r=stddev and theta=arccos(correlation).
    """

    def __init__(self, modelData):
        self.modelData = numpy.asarray(modelData)

    def setup_axes(self, fig, rect=111):
        """Set up Taylor diagram axes, i.e. single quadrant polar
        plot, using mpl_toolkits.axisartist.floating_axes.
        """

        from matplotlib.projections import PolarAxes
        import mpl_toolkits.axisartist.floating_axes as FA
        import mpl_toolkits.axisartist.grid_finder as GF

        tr = PolarAxes.PolarTransform()

        # Correlation labels
        rlocs = numpy.concatenate((numpy.arange(10) / 10., [0.95, 0.99]))
        tlocs = numpy.arccos(rlocs)        # Conversion to polar angles
        gl1 = GF.FixedLocator(tlocs)    # Positions
        tf1 = GF.DictFormatter(dict(zip(tlocs, map(str, rlocs))))

        ghelper = FA.GridHelperCurveLinear(tr,
            extremes=(0, numpy.pi / 2, # 1st quadrant
                      0, 1.5 * self.modelData.std()),
            grid_locator1=gl1,
            tick_formatter1=tf1,
        )

        ax = FA.FloatingSubplot(fig, rect, grid_helper=ghelper)
        fig.add_subplot(ax)

        # Adjust axes
        ax.axis["top"].set_axis_direction("bottom")  # "Angle axis"
        ax.axis["top"].toggle(ticklabels=True, label=True)
        ax.axis["top"].major_ticklabels.set_axis_direction("top")
        ax.axis["top"].label.set_axis_direction("top")
        ax.axis["top"].label.set_text("Correlation coefficient")

        ax.axis["left"].set_axis_direction("bottom") # "X axis"
        ax.axis["left"].label.set_text("Standard deviation")

        ax.axis["right"].set_axis_direction("top")   # "Y axis"
        ax.axis["right"].toggle(ticklabels=True)
        ax.axis["right"].major_ticklabels.set_axis_direction("left")

        ax.axis["bottom"].set_visible(False)         # Useless

        # Grid
        ax.grid()

        self._ax = ax                   # Graphical axes
        self.ax = ax.get_aux_axes(tr)   # Polar coordinates

        # Add reference point and stddev contour
        print "Reference std:", self.modelData.std()
        self.ax.plot([0], self.modelData.std(), 'ko', label='_')
        t = numpy.linspace(0, numpy.pi / 2)
        r = numpy.zeros_like(t) + self.modelData.std()
        self.ax.plot(t, r, 'k--', label='_')

        return self.ax

    def get_coords(self, sample):
        """Computes theta=arccos(correlation) and rad=stddev of sample
        according to model data."""

        standardDeviation = numpy.std(sample)
        correlationCoefficient = numpy.corrcoef(self.modelData, sample) # [[1,rho],[rho,1]]
        theta = numpy.arccos(correlationCoefficient[0, 1])

#        print "Sample standardDeviation, rho:", standardDeviation, correlationCoefficient[0, 1]

        return theta, standardDeviation

    def plot_sample(self, sample, *args, **kwargs):
        """Add sample to the Taylor diagram. args and kwargs are
        directly propagated to the plot command."""

        theta, radius = self.get_coords(sample)
        self.ax.plot(theta, radius, *args, **kwargs) # (theta,radius)


def exportTaylorDiagram(targetFile, values, referenceValues):
    diagram = TaylorDiagram(values)
    figure = pyplot.figure()

    diagram.setup_axes(figure, 111)
    diagram.plot_sample(referenceValues, 'yh')

    pyplot.savefig(targetFile)
