import sys
import os

# Define absolute base paths to avoid CWD reference issues
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

INPUT_DIR = os.path.join(BASE_DIR, 'data', 'input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'output')

from method.MATSGT import MATSGT
from method.MATSG import MATSG
from model import *
from model.Util import *
from method.MUITAS import MUITAS
import numpy

a = MATSGT(
    trc=0.25,
    trv=0.25,
    path=os.path.join(INPUT_DIR, 'Running_Example_v5.csv')
)

a.execute(
    lst_categorical_pd=['price'],
    values_null=[-1],
    pattern_date_input='?',
    dir=f"{OUTPUT_DIR}/",
    file='teste',
    rc=0.25,
    trv=0.25,
    ignore_columns=None
)