from setuptools import setup

setup(name='opec',
    version='0.1',
    description='The Benchmarking Tool of the EU Operational Ecology project, OpEc',
    author='Thomas Storm',
    author_email='thomas.storm@brockmann-consult.de',
    url='http://marine-opec.eu/',
    packages=['opec'],
    data_files=[('opec', ['opec/default.properties'])],
    requires=['numpy (>= 1.6.2)',
              'scipy (>= 0.11.0)',
              'netCDF4 (>= 1.0.1)',
              'nose (>= 1.2.1)',
              'mako (>= 0.7.3)',
              'matplotlib (>= 1.2.0)']
)
