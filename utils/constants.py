import datetime
import pandas as pd
from .candidate import Candidate

STARTDATE = pd.tslib.Timestamp(datetime.datetime(year=2017, month=3, day=20))
FIRST_ROUND = pd.tslib.Timestamp(datetime.datetime(year=2017, month=4, day=23))
SECOND_ROUND = pd.tslib.Timestamp(datetime.datetime(year=2017, month=5, day=8))

CANDIDATES_1ST_ROUND = list(map(Candidate, ['LEPEN', 'MACRON', 'HAMON', 'MELENCHON', 'FILLON', 'POUTOU', 'ASSELINEAU', 'DUPONT', 'ARTHAUD', 'CHEMINADE', 'LASSALLE']))
CANDIDATES_2ND_ROUND = list(map(Candidate, ['LEPEN', 'MACRON']))
