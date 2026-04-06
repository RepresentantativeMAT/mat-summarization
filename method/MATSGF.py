import math
from typing import List, Tuple
from collections import defaultdict
from method.MATSummarize import MATSummarize
from method.FeatureAggregator import FeatureAggregator
from model import Point, Centroid, SemanticAspect, SemanticType, Feature
from model.Util import time_to_minutes

class MATSGF(MATSummarize):
    def __init__(self, trc, trv, path, features: List[Feature] = None):
        super().__init__(trc, trv, path)
        self.features = features if features else []
        self._feature_aspects = {} # Map feature name to SemanticAspect

    def load(self, path, ignore_columns=None, force_cat_columns=None, values_null=None):
        super().load(path, ignore_columns, force_cat_columns, values_null)
        
        # Add features as special categorical aspects after standard data loading
        order = len(self._aspects)
        for feature in self.features:
            aspc = SemanticAspect(feature.name, order, SemanticType.CATEGORICAL)
            self._aspects.append(aspc)
            self._feature_aspects[feature.name] = aspc
            order += 1

    def process_cell_points(self, cell_points: List[Point], cell_id: Tuple[int, int]):
        """
        Mimics MATSG logic to create a single centroid per cell.
        """
        times = []
        rp = Centroid()
        rp.cell_reference = str(cell_id)
        
        # 1. Fuse all points geometrically and semantically
        for p in cell_points:
            rp.add_point(p)
            self._avg_x += p.x
            self._avg_y += p.y
            times.append(time_to_minutes(p.time.start_time))
            self.fuse_aspects(p)
            
        rp.x = self._avg_x / len(cell_points)
        rp.y = self._avg_y / len(cell_points)
            
        # 2. Temporal calculation
        temporal_ranking_map = self._define_ranking_temporal(times)
        normalized_time = self.normalize_ranking_values(temporal_ranking_map, len(cell_points), 't', self._consider_nulls)
        
        time_aspect = SemanticAspect("TIME", order=-1, type=SemanticType.CATEGORICAL)
        rp.add_attr_value(normalized_time, time_aspect)
        
        self._list_rep_point.append(rp)

    def process_representative_point(self, rep_point: Centroid):
        """
        Hook called after standard attribute summarization.
        Extracts complex features and adds them to the representative point.
        """
        if not self.features:
            return
            
        cell_points = rep_point.point_list_source
        
        # 1. Feature Aggregation
        extracted_counts = FeatureAggregator.extract_features(cell_points, self.features)
        
        # 2. Compute Distribution
        distributions = FeatureAggregator.compute_feature_distribution(
            extracted_counts, 
            len(cell_points), 
            self._trv, 
            self._consider_nulls,
            self._null_value
        )
        
        # 3. Compress Features
        compressed_dist = FeatureAggregator.compress_features(distributions)
        
        # 4. Attach to Rep Point
        for feature_name, dist in compressed_dist.items():
            aspect = self._feature_aspects[feature_name]
            rep_point.add_attr_value(dist, aspect)

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
