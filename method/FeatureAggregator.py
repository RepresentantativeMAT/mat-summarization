from typing import List, Dict, Any, Tuple
from collections import defaultdict
from model.Point import Point
from model.Feature import Feature

class FeatureAggregator:

    @staticmethod
    def extract_features(cell_points: List[Point], features: List[Feature]) -> Dict[str, Dict[Tuple[str, ...], int]]:
        """
        Extracts features from a list of points and computes their absolute frequency.
        """
        feature_counts = {f.name: defaultdict(int) for f in features}
        
        for point in cell_points:
            for feature in features:
                val_tuple = feature.extract_from_point(point)
                feature_counts[feature.name][val_tuple] += 1
                
        return feature_counts

    @staticmethod
    def compute_feature_distribution(feature_counts: Dict[str, Dict[Tuple[str, ...], int]], 
                                     total_points: int, 
                                     trv: float, 
                                     consider_nulls: bool = True,
                                     null_value: str = 'UNKNOWN') -> Dict[str, Dict[Tuple[str, ...], float]]:
        """
        Computes proportional distribution and filters those with `value >= trv`.
        """
        distributions = {}
        for feature_name, counts in feature_counts.items():
            valid_map = {}
            valid_pts = 0
            
            # Simple approach logic similar to the existing norm logic
            if consider_nulls:
                for val_tuple, freq in counts.items():
                    trend_val = freq / total_points
                    if trend_val >= trv:
                        valid_pts += freq
                        valid_map[val_tuple] = freq
                
                new_map = {}
                if valid_pts > 0:
                    for val_tuple, freq in valid_map.items():
                        new_map[val_tuple] = freq / valid_pts
                distributions[feature_name] = new_map
            else:
                size_not_null = total_points
                # Subtract records where ALL elements in tuple are null_value
                null_tuple_count = 0
                for val_tuple, freq in counts.items():
                    if all(v == null_value for v in val_tuple):
                        null_tuple_count += freq
                size_not_null -= null_tuple_count
                
                new_map = {}
                if size_not_null > 0:
                    for val_tuple, freq in counts.items():
                        if not all(v == null_value for v in val_tuple):
                            trend_val = freq / size_not_null
                            if trend_val >= trv:
                                new_map[val_tuple] = trend_val
                
                distributions[feature_name] = new_map
                
            distributions[feature_name] = dict(sorted(distributions[feature_name].items(), key=lambda item: item[1], reverse=True))

        return distributions

    @staticmethod
    def compress_features(feature_distribution: Dict[str, Dict[Tuple[str, ...], float]]) -> Dict[str, Dict[Tuple[str, ...], float]]:
        """
        Optional semantic compression combining highly similar sub-features based on numerical dimensions.
        (Placeholder for future expansion, returns the input as-is for now)
        """
        # Compress logic can be added here
        return feature_distribution
