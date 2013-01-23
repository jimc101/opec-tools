from opec import Utils
import logging
from opec import Processor
from opec.Configuration import Configuration
from opec.Data import Data
from opec.MatchupEngine import MatchupEngine
from opec.Output import Output

handler = logging.StreamHandler()
handler.setFormatter(Utils.get_logging_formatter())
logging.getLogger().addHandler(handler)

def load(filename):
    return Data(filename)

def calculate_statistics(model_name, ref_name, data, config=None):
    me = MatchupEngine(data, config)
    matchups = me.find_all_matchups()
    return calculate_statistics_from_matchups(matchups, model_name, ref_name, config=None)

def calculate_statistics_from_matchups(matchups, model_name, ref_name, config=None):
    return Processor.calculate_statistics(matchups, model_name, ref_name, config=config)

def calculate_statistics_from_values(model_values, ref_values, config=None):
    return Processor.calculate_statistics(model_values=model_values, reference_values=ref_values, config=config)

def get_matchups(data, config=None):
    me = MatchupEngine(data, config)
    return me.find_all_matchups()

def extract_values(model_name, ref_name, data):
    ma = get_matchups(data)
    return extract_values_from_matchups(ma, model_name, ref_name)

def extract_values_from_matchups(matchups, model_name, ref_name):
    return Processor.extract_values(matchups, ref_name, model_name)

def write_csv(statistics, model_name, ref_name, matchups, target_file, config=None):
    op = Output(config=config)
    op.csv(statistics, model_name, ref_name, matchups, target_file)

def write_taylor_diagram(statistics, target_file, config=None):
    op = Output(config=config)
    op.taylor([statistics], target_file)