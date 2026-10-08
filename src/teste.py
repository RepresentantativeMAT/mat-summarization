import pandas as pd
import numpy as np
from mat_summarize.method import MATSGT

model_sgt = MATSGT(
    trc=0.25,
    trv=0.25,
    path='data/input/Running_Examples/Running_Example_v5.csv'
)

model_sgt.execute(
    lst_categorical_pd=['price'],
    values_null=[-1, -999],
    dir='data/',
    file='Running_Example_v5',
    ignore_columns=None,
    features=[('poi',), ('price',), ('weather', 'precip')]
)