from opec import Utils
import logging

__author__ = 'Thomas Storm'

handler = logging.StreamHandler()
handler.setFormatter(Utils.get_logging_formatter())
logging.getLogger().addHandler(handler)
