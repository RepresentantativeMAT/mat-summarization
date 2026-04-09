import sys
import os

# Add the project root to sys.path if not running from root module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from method.MATSG import MATSG
from method.MATSGT import MATSGT
from method.MUITAS import MUITAS
from model.Feature import Feature

def test():
    
    matsgf = MATSGT(
        trc=0.25,
        trv=0.25, 
        path="data/input/Running_Example_v5.csv"
    )
    
    matsgf.execute(
        dir="data/output/", 
        file="MATSGT_out", 
        lst_categorical_pd=['price'],
        values_null=['-1'], 
        ignore_columns=None,
        pattern_date_input='?', 
        rc=0.25, 
        trv=0.25
    )
    print("Execution Finished!")

if __name__ == "__main__":
    test()


