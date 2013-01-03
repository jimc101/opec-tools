from datetime import datetime
from unittest import TestCase
from src.main.python import Processor
from src.main.python.Data import Data
from src.main.python.Matchup import Matchup
from src.main.python.Output import Output

class OutputTest(TestCase):

    def test_output_basic_statistics_from_dictionary(self):

        matchups = [
            Matchup('chl_ref', 'chl', 10, 11, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 9, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 11.2, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 10.5, 55, 20, 10000, 0, 0, 0, 0.1, 0)
        ]
        stats = Processor.basic_statistics(matchups)

        output = Output(
            statistics=stats,
            variable_name='chl',
            ref_variable_name='chl_ref',
            matchup_count=4,
            macro_pixel_size=123,
            geo_delta=12,
            time_delta=1234,
            depth_delta=0.234,
            source_file='somethingsomethingsomethingdarkside',
        )

        expected_result = []
        now = datetime.now()
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Benchmarking results of file \'somethingsomethingsomethingdarkside\'")
        expected_result.append("#")
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Created on {} {}, {} at {}:{}:{}".format(now.month, now.day, now.year, now.hour, now.minute, now.second))
        expected_result.append("#")
        expected_result.append("# Matchup criteria:")
        expected_result.append("#    Macro pixel size = 123")
        expected_result.append("#    Maximum geographic delta = 12 \"degrees\"")
        expected_result.append("#    Maximum time delta = 1234 seconds")
        expected_result.append("#    Maximum depth delta = 0.234 meters")
        expected_result.append("#")
        expected_result.append("variable_name\tref_variable_name\tmatchup_count\tmin\tmax\tmean\tstddev\tmedian\tp90\tp95\tref_min\tref_max\tref_mean\tref_stddev\tref_median\tref_p90\tref_p95\trmsd\tunbiased_rmsd\tbias\tpbias\tcorrcoeff\treliability_index\tmodel_efficiency")
        expected_result.append("chl\tchl_ref\t4\t9\t11.2\t10.425\t0.8613\t10.75\t11.14\t11.17\t10\t10\t10\t0\t10\t10\t10\t0.9605\t0.8613\t-0.425\t-4.25\tnan\t1.0417\tnan")

        print("\n".join(expected_result))

        print(output.csv())

        self.assertEqual("\n".join(expected_result), output.csv())

    def test_output_basic_statistics_from_dictionary_minimum(self):

        matchups = [
            Matchup('chl_ref', 'chl', 10, 11, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 9, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 11.2, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 10.5, 55, 20, 10000, 0, 0, 0, 0.1, 0)
        ]
        stats = Processor.basic_statistics(matchups)

        output = Output(statistics=stats)

        expected_result = []
        now = datetime.now()
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Benchmarking results")
        expected_result.append("#")
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Created on {} {}, {} at {}:{}:{}".format(now.month, now.day, now.year, now.hour, now.minute, now.second))
        expected_result.append("#")
        expected_result.append("variable_name\tref_variable_name\tmatchup_count\tmin\tmax\tmean\tstddev\tmedian\tp90\tp95\tref_min\tref_max\tref_mean\tref_stddev\tref_median\tref_p90\tref_p95\trmsd\tunbiased_rmsd\tbias\tpbias\tcorrcoeff\treliability_index\tmodel_efficiency")
        expected_result.append("None\tNone\tNone\t9\t11.2\t10.425\t0.8613\t10.75\t11.14\t11.17\t10\t10\t10\t0\t10\t10\t10\t0.9605\t0.8613\t-0.425\t-4.25\tnan\t1.0417\tnan")

        self.assertEqual("\n".join(expected_result) , output.csv())
        
    def test_output_basic_statistics_from_dictionary_no_header(self):

        matchups = [
            Matchup('chl_ref', 'chl', 10, 11, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 9, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 11.2, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 10.5, 55, 20, 10000, 0, 0, 0, 0.1, 0)
        ]
        stats = Processor.basic_statistics(matchups)

        output = Output(statistics=stats)

        expected_result = []
        expected_result.append("variable_name;ref_variable_name;matchup_count;min;max;mean;stddev;median;p90;p95;ref_min;ref_max;ref_mean;ref_stddev;ref_median;ref_p90;ref_p95;rmsd;unbiased_rmsd;bias;pbias;corrcoeff;reliability_index;model_efficiency")
        expected_result.append("None;None;None;9;11.2;10.425;0.8613;10.75;11.14;11.17;10;10;10;0;10;10;10;0.9605;0.8613;-0.425;-4.25;nan;1.0417;nan")

        self.assertEqual("\n".join(expected_result) , output.csv(False, ';'))

    def test_output_basic_statistics_from_data(self):
        data = Data('../resources/test.nc')
        output = Output(data=data, variable_name='chl', ref_variable_name='chl_ref')

        expected_result = []
        now = datetime.now()
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Benchmarking results")
        expected_result.append("#")
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Created on {} {}, {} at {}:{}:{}".format(now.month, now.day, now.year, now.hour, now.minute, now.second))
        expected_result.append("#")
        expected_result.append("variable_name\tref_variable_name\tmatchup_count\tmin\tmax\tmean\tstddev\tmedian\tp90\tp95\tref_min\tref_max\tref_mean\tref_stddev\tref_median\tref_p90\tref_p95\trmsd\tunbiased_rmsd\tbias\tpbias\tcorrcoeff\treliability_index\tmodel_efficiency")
        expected_result.append("chl\tchl_ref\t56\t0.1111\t")

        print(output.csv())

        self.assertTrue(output.csv().startswith("\n".join(expected_result)))

    def test_wrong_initialisation_1(self):
        with self.assertRaises(ValueError):
            Output()

    def test_wrong_initialisation_2(self):
        with self.assertRaises(ValueError):
            Output(data='dummy_data')

    def test_wrong_initialisation_3(self):
        with self.assertRaises(ValueError):
            Output(data='dummy_data', ref_variable_name='ref')

    def test_wrong_initialisation_4(self):
        with self.assertRaises(ValueError):
            Output(data='dummy_data', variable_name='var')
