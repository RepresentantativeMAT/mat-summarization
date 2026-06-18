import math
import numpy as np
from typing import List, Tuple
from method.MATSummarize import MATSummarize
from model import Point, TemporalAspect, STI, Centroid
from model.Util import time_to_minutes, remove_outliers

class MATSGT(MATSummarize):
    
    def process_cell_points(self, cell_points: List[Point], cell_id: Tuple[int, int]):
        """
        MATSGT Hook Implementation:
        Find STIs inside the cell and generate one Centroid for each expressive STI.
        """
        times = [p.time.start_time for p in cell_points]
        stis = []
            
        # 1. Extract Significant Temporal Intervals
            
        self.summarize_temporal_aspect(times, stis)
        
        # 2. Create N representative points (Centroids) chronologically
        for interval in stis:
            if interval.proportion >= self._trv:
                rp = Centroid()
                rp.cell_reference = cell_id
                rp.sti = interval
                
                # Link only points corresponding to this STI
                self.reset_values_to_summarization()
                for vp in cell_points:
                    if interval.interval.is_in_interval(vp.time.start_time):
                        rp.add_point(vp)
                        # We must fuse ONLY the aspects of points that actually belong to this Centroid
                        # To prevent contamination of categoric counts from points outside this STI interval in the same cell

                if rp.point_list_source:
                    self._list_rep_point.append(rp)

    def summarize_temporal_aspect(self, time_in_points: list, stis: list):
        time_in_points.sort()
        differences = self.compute_time_differences(time_in_points)

        threshold_differences = 100
        if len(differences) > 2:
            median = np.median(differences)
            sd_deviation = np.std(differences, ddof=1)

            lower_value = median - sd_deviation
            upper_value = median + sd_deviation

            valid_differences = remove_outliers(differences, lower_value, upper_value)
            threshold_differences = math.floor(np.mean(valid_differences))
        
        self.create_temporal_intervals(time_in_points, stis, threshold_differences)
        self.asort_temporal_intervals(stis)

    def compute_time_differences(self, tip: list) -> list:
        minutes_list = [time_to_minutes(t) for t in tip]
        differences = [minutes_list[i] - minutes_list[i-1] for i in range(1, len(minutes_list)) if minutes_list[i] - minutes_list[i-1] > 0]
        return differences
    
    def create_temporal_intervals(self, tip: list, stis: list, threshold: float):
        count = 1
        current_interval = None

        for i in range(0, len(tip)):
            if i != len(tip) - 1 and time_to_minutes(tip[i]) + 58 >= time_to_minutes(tip[i + 1]):
                if current_interval is None:
                    current_interval = TemporalAspect(tip[i])
                count += 1
            else:
                if current_interval is None:
                    current_interval = TemporalAspect(tip[i])
                else:
                    current_interval.end_time = tip[i]
                stis.append(STI(current_interval, count / len(tip)))
                count = 1
                current_interval = None
        # print("DEBUG STIs generated:", [str(sti) + " prop: " + str(sti.proportion) for sti in stis])

    def asort_temporal_intervals(self, stis: list):
        stis.sort(key=lambda sti: sti.proportion, reverse=True)