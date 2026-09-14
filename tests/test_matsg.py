import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ..src.mat_summarize.method.MATSG import MATSG

def test():
    
    matsgf = MATSG(
        trc=0.25,
        trv=0.25, 
        path="../data/input/Running_Example_v5.csv"
    )
    
    matsgf.execute(
        dir="data/output/", 
        file="MATSG_out", 
        lst_categorical_pd=['price'],
        values_null=['-1'], 
        ignore_columns=None,
        pattern_date_input='?', 
        rc=0.25, 
        trv=0.25,
        features=[('poi',), ('price',), ('weather',), ('precip',)]
    )
    print("Execution Finished!")

if __name__ == "__main__":
    test()


