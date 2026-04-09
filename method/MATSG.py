import math
import numpy as np
from typing import List, Tuple
from collections import defaultdict
from method.MATSummarize import MATSummarize
from model import Point, Centroid, SemanticAspect, SemanticType
from model.Util import time_to_minutes, minutes_to_time

class MATSG(MATSummarize):
    
    def process_cell_points(self, cell_points: List[Point], cell_id: Tuple[int, int]):
        """
        MATSG Hook Implementation:
        Generate exactly 1 Centroid for the entire cell and compute Time distribution.
        """
        times = []
        rp = Centroid()
        rp.cell_reference = cell_id
        
        # 1. Fuse all points geometrically and semantically
        for p in cell_points:
            rp.add_point(p)
            self._avg_x += p.x
            self._avg_y += p.y
            times.append(time_to_minutes(p.time.start_time))
            self.fuse_aspects(p)
            
        rp.x = self._avg_x / len(cell_points)
        rp.y = self._avg_y / len(cell_points)
            
        self.summarize_numerical_aspects(rp)
        self.summarize_categorical_aspects(rp)
        
        # 2. Extract Temporal Aggregate specifically for MATSG 
        temporal_ranking_map = self._define_ranking_temporal(times)
        normalized_time = self.normalize_ranking_values(temporal_ranking_map, len(cell_points), 't', self._consider_nulls)
        
        # Insert Faked Temporal Dimension
        time_aspect = SemanticAspect("TIME", type=SemanticType.CATEGORICAL)
        rp.add_feat_value(normalized_time, (time_aspect,))
        
        self._list_rep_point.append(rp)
        
    def _define_ranking_temporal(self, times_in_cell: List[int]) -> dict:
        times_in_cell.sort()
        differences = []
        sum_differences = 0
        threshold = 100
        
        for i in range(1, len(times_in_cell)):
            diff = times_in_cell[i] - times_in_cell[i - 1]
            differences.append(diff)
            sum_differences += diff
            
        if len(differences) > 1:
            avg = sum_differences / len(differences)
            sum_differences = 0
            differences.sort()
            
            if len(differences) > 2:
                # Find Median
                if len(differences) % 2 == 1:
                    med = differences[len(differences) // 2]
                else:
                    med = (differences[len(differences) // 2 - 1] + differences[len(differences) // 2]) / 2
                    
                # Find Standard Deviation
                for diff in differences:
                    sum_differences += (diff - avg) ** 2
                sd = math.sqrt(sum_differences / len(differences))
                
                less_val = med - sd
                upper_val = med + sd
                
                sum_differences = 0
                valid_diff_size = 0
                
                for diff in differences:
                    if less_val <= diff <= upper_val:
                        sum_differences += diff
                        valid_diff_size += 1
                        
                if valid_diff_size > 0:
                    threshold = math.floor(sum_differences / valid_diff_size)
        
        aux = None
        cont = 1
        temporal_ranking = defaultdict(int)
        
        for i in range(len(times_in_cell)):
            if i != len(times_in_cell) - 1 and (times_in_cell[i] + threshold) >= times_in_cell[i + 1]:
                if aux is None:
                    aux = str(times_in_cell[i])
                cont += 1
            else:
                if aux is None:
                    aux = str(times_in_cell[i])
                else:
                    aux += "-" + str(times_in_cell[i])
                    
                temporal_ranking[aux] = cont
                cont = 1
                aux = None
                
        return dict(temporal_ranking)
