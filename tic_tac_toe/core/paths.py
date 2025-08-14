from pathlib import Path

# Project root (goes up from /core to the tic_tac_toe folder)
ROOT_PATH = Path(__file__).resolve().parent.parent
ROOT_PATH_DATA = ROOT_PATH / 'data'
ROOT_PATH_LOGS = ROOT_PATH_DATA / 'logs'
ROOT_PATH_USER_CONFIG = ROOT_PATH / 'user_config'
ROOT_PATH_RANKING = ROOT_PATH_DATA / 'ranking'

# File names
DB_NAME = 'credentials.shlv'
DB_PATH = ROOT_PATH_DATA / DB_NAME
DEFAULT_LOGS_FILE = 'tic_tac_toe_logs.txt'
LOGS_FILE = 'logs_file'
RANKING_PLAYERS_SHELVE = 'ranking_top_players.shlv'
