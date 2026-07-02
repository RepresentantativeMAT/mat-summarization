import csv
import copy
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
import numpy as np
import math
from collections import defaultdict, Counter
from scipy.spatial import cKDTree
from model import MultipleAspectTrajectory, SemanticAspect, SemanticType, Point, TemporalAspect, STI, Centroid
from model.Util import time_to_minutes, minutes_to_time, remove_outliers
from .MUITAS import MUITAS

class MATSummarize(ABC):
    def __init__(self, trc, trv, path):
        ## Attributes
        self._consider_nulls = True
        self._daily_info = False
        self._rc = 0
        self._directory = ''
        self._filename = ''
        self._path = path
        self._initial_temp = None
        ## MAT-SG
        self._trc = trc
        self._trv = trv
        ## Load
        self._aspects = []
        self._features = [] #aspect groups
        self._points = []
        self._spatial_cell_grid = defaultdict(list)
        ## Summarization Step
        self._null_value = 'UNKNOWN'
        self._representative_trajectory = None
        self._list_rep_point = []
        self._semantic_numeric_fusion_val = defaultdict(list)
        self._semantic_categorical_summarization_val = defaultdict(Counter)
        self._avg_x = 0
        self._avg_y = 0
        ## Spatial Segmentation
        self._spatial_threshold = 0.0
        self._cell_size_space = 1.0
        ## AUX
        self._dataset = []
        self._better_rt = MultipleAspectTrajectory
        self._aux_max_z = 0.0

    def load(self, path, ignore_columns = None, force_cat_columns = None, values_null = None, features=list[tuple[SemanticAspect, ...]]):
        always_ignore = ['tid', 'lat_lon', 'time', 'label', 'x', 'y']
        df = pd.read_csv(path)

        if ignore_columns:
            df.drop(columns=ignore_columns, inplace=True, errors='ignore')
        
        aspects_map = {}
        for column in df.columns:
            if force_cat_columns and column in force_cat_columns:
                aspc = SemanticAspect(column, SemanticType.CATEGORICAL)
                self._aspects.append(aspc)
                aspects_map[column] = aspc
            elif column not in always_ignore:
                aspc = SemanticAspect(
                    column,
                    SemanticType.CATEGORICAL if not pd.api.types.is_numeric_dtype(df[column]) else SemanticType.NUMERICAL
                )
                self._aspects.append(aspc)
                aspects_map[column] = aspc
        
        for i in df['tid'].unique():
            self._dataset.append(MultipleAspectTrajectory(None, i))

        df[['x', 'y']] = df['lat_lon'].str.split(' ', expand=True).astype(float)

        semantic_columns = [c for c in df.columns if c in aspects_map]

        for feat in features:
            feat_list = []
            for name in feat:
                feat_list.append([a for a in self._aspects if a.name == name.upper()][0])
            self._features.append(tuple(sorted(feat_list, key=lambda aspect: aspect.type)))

#provavel alteracao para utilizar FEATURES
        rid = 1
        idx = 0
        tid_anterior = float('-inf')
        df = df.sort_values(by='tid')
        for row in df.itertuples(index=False):
            if (tid_anterior == float('-inf')):
                tid_anterior = row.tid

            semantics = {}
            fsemantics = {}

            for fgroup in self._features:
                fsemantics[fgroup] = []
                for feat in range(len(fgroup)):
                    fsemantics[fgroup].append(None)

            for c in semantic_columns:
                v = getattr(row, c)
                aspc = aspects_map[c]
                if aspc.type == SemanticType.CATEGORICAL and isinstance(v, (int, float)):
                    if isinstance(v, float) and v.is_integer():
                        v = int(v)
                    v = '*' + str(v)
                elif aspc.type == SemanticType.CATEGORICAL and isinstance(v, str):
                    v = v.upper()
                semantics[aspc] = v

                for fgroup in self._features:
                    for feat in range(len(fgroup)):
                        if fgroup[feat].name == aspc.name:
                            fsemantics[fgroup][feat] = v

            for feat in fsemantics:
                if len(feat) > 1:
                    fsemantics[feat] = [', '.join(map(str, fsemantics[feat]))]

            if (tid_anterior != row.tid):
                tid_anterior = row.tid
                idx += 1

            p = Point(None, rid, row.x, row.y, row.date_time, None, fsemantics)
            self._points.append(p)
            self._dataset[idx].add_point(p)
            rid += 1
#-----------------------------------------

    def compute_min_spatial_threshold(self):
        if not self._points:
            return

        coords = np.array([[p.x, p.y] for p in self._points])
        
        #? np.linalg.norm() calcula a distância euclidiana
        #? de cada uma das coordenadas com o ponto (0, 0)
        distances_to_origin = np.linalg.norm(coords, axis=1)
        max_distance_to_zero = np.max(distances_to_origin)

        if len(coords) > 1:
            tree = cKDTree(coords)
            k = len(coords)
            distances, _ = tree.query(coords, k=k)
            valid_distances = np.array([
                row[row > 0][0]
                for row in distances
                if np.any(row > 0)
            ])
            
            median_min_dist = np.median(valid_distances)
            sd_min_dist = np.std(valid_distances)

            less_value_min_dist = median_min_dist - 4 * sd_min_dist
            upper_value_min_dist = median_min_dist + 4 * sd_min_dist

            valid_distances_without_outliers = valid_distances[
                (valid_distances >= less_value_min_dist) & 
                (valid_distances <= upper_value_min_dist) & 
                (valid_distances != 0.0)
            ]

            if len(valid_distances_without_outliers) > 0:
                self._spatial_threshold = float(np.mean(valid_distances_without_outliers))
                self._aux_max_z = float(max_distance_to_zero / self._spatial_threshold)

    def get_cell_position(self, x, y):
        return (math.floor(x / self._cell_size_space), math.floor(y / self._cell_size_space))
    
    def allocate_in_space_cell(self, point):
        key = self.get_cell_position(point.x, point.y)
        self._spatial_cell_grid[key].append(point.rid)

    def allocate_all_points_in_space_cell(self):
        for p in self._points:
            self.allocate_in_space_cell(p)

    def identify_and_process_cells(self):
        self._list_rep_point.clear()

        for k, v in self._spatial_cell_grid.items():
            cell_analyzed = k
            qtd_points = len(self._spatial_cell_grid[cell_analyzed])

            if qtd_points >= self._trc:
                self.reset_values_to_summarization()
                
                # Fetch Points sequentially
                cell_points = []
                for point_id in sorted(self._spatial_cell_grid[cell_analyzed]):
                    cell_points.append(self._points[point_id-1])
                

                # TEMPLATE METHOD HOOK
                self.process_cell_points(cell_points, cell_analyzed)

        # After all cells processed, add generated centroids to global representative trajectory list sorting by proportion
        self._list_rep_point.sort(reverse=True)
        for rep in self._list_rep_point:
            self.reset_values_to_summarization()

            self._representative_trajectory.add_point(rep)
            self._representative_trajectory.increment_value(len(rep.point_list_source))
            
            for p in rep.point_list_source:
                self._avg_x += p.x
                self._avg_y += p.y
                self.fuse_aspects(p)
                
            rep.x = self._avg_x / len(rep.point_list_source)
            rep.y = self._avg_y / len(rep.point_list_source)

            self.summarize_numerical_aspects(rep)
            self.summarize_categorical_aspects(rep)
            self.process_representative_point(rep)
            
        self.reset_values_to_summarization()

    def process_representative_point(self, rep_point):
        # Template hook for subclasses to apply extra processing to the generated Rep Point
        pass

    @abstractmethod
    def process_cell_points(self, cell_points, cell_id):
        pass

    def reset_values_to_summarization(self):
        self._avg_x = 0
        self._avg_y = 0
        self._semantic_numeric_fusion_val.clear()
        self._semantic_categorical_summarization_val.clear()
        

    def fuse_aspects(self, point):
        values_num_invalid = self._values_null if hasattr(self, '_values_null') and self._values_null else []

        for ftv in point.list_feat_values.items():
            feat_current = ftv[0]

            for i in range(len(ftv[0])):
                try: 
                    val = float(str(ftv[1][0]))
                    self._features[self._features.index(ftv[0])][i].type = SemanticType.NUMERICAL
                
                    if val not in values_num_invalid:
                        self._semantic_numeric_fusion_val[feat_current].append(val)
                except ValueError:
                    if self._features[self._features.index(ftv[0])][i].type is None or self._features[self._features.index(ftv[0])][i].type != SemanticType.NUMERICAL:
                        self._features[self._features.index(ftv[0])][i].type = SemanticType.CATEGORICAL
                        self._semantic_categorical_summarization_val[ftv[0]][ftv[1][0]] += 1

    def summarize_numerical_aspects(self, rep_point):
        for k, v in self._semantic_numeric_fusion_val.items():
            median = float('-inf')
            new_map = {}

            if self._consider_nulls:
                if len(rep_point.point_list_source) - len(v) == len(v):
                    null_str = str(self._values_null[0]) if hasattr(self, '_values_null') and self._values_null else '-999.0'
                    new_map[null_str] = 0.5
                    median = float(np.median(v))
                    new_map[str(median)] = 0.5
                elif len(rep_point.point_list_source) - len(v) < len(v):
                    median = float(np.median(v))
            else:
                if v:
                    median = float(np.median(v))

            if not new_map:
                rep_point.add_feat_value(median, self._features[self._features.index(k)])
            else:
                rep_point.add_feat_value(new_map, self._features[self._features.index(k)])

    def summarize_categorical_aspects(self, rep_point):
        for k, im in self._semantic_categorical_summarization_val.items():
            internal_categorical_list = dict(sorted(im.items(), key=lambda item: item[1], reverse=True))
            rep_point.add_feat_value(
                self.normalize_ranking_values(internal_categorical_list, len(rep_point.point_list_source), 's', self._consider_nulls),
                self._features[self._features.index(k)]
            )

    def normalize_ranking_values(self, map_rank, mapped_pts, dimension, consider_nulls=True):
        if not map_rank:
            raise ValueError("Invalid input: map_rank must not be null or empty.")
        if mapped_pts <= 0:
            raise ValueError("Invalid input: mapped_pts must be a positive value.")
        
        new_map = {}
        
        if consider_nulls:
            valid_pts = 0
            for k, v in map_rank.items():
                trend_val = float(v) / mapped_pts
                if trend_val >= self._trv:
                    valid_pts += v
                else:
                    map_rank[k] = -1

            for k, v in map_rank.items():
                if v != -1:
                    new_map[k] = v / valid_pts
        else:
            size_not_null = mapped_pts
            if self._null_value in map_rank:
                size_not_null -= map_rank[self._null_value]

            if size_not_null < mapped_pts:
                for k, v in map_rank.items():
                    if str(k).lower() != 'unknown':
                        trend_val = float(v) / size_not_null
                        if trend_val >= self._trv:
                            new_map[k] = trend_val
            else:
                for k, v in map_rank.items():
                    trend_val = float(v) / size_not_null
                    if trend_val >= self._trv:
                        new_map[k] = trend_val
        
        new_map_sorted = dict(sorted(new_map.items(), key=lambda x: x[1], reverse=True))

        if dimension[0].lower() == 't':
            new_time_map = {}
            for k, v in new_map_sorted.items():
                interval_str = str(k)
                if '-' in interval_str:
                    s, e = interval_str.split('-')
                    aux_interval = f"{minutes_to_time(int(s)).strftime('%H:%M')} - {minutes_to_time(int(e)).strftime('%H:%M')}"
                else:
                    aux_interval = minutes_to_time(int(interval_str)).strftime('%H:%M')
                
                new_time_map[aux_interval] = v
            return new_time_map
        
        return new_map_sorted

    def execute(self, dir, file, lst_categorical_pd, values_null, ignore_columns, pattern_date_input, rc, features:list[tuple[SemanticAspect, ...]]):
        self._initial_temp = datetime.today()
        self._directory = dir
        self._filename = file
        self._values_null = [float(x) for x in values_null] if values_null is not None else []
        self._representative_trajectory = MultipleAspectTrajectory('representative')

        if pattern_date_input == '?':
            self._representative_trajectory.daily_info = True
            self._daily_info = True

        self._spatial_cell_grid = defaultdict(list)
        self._semantic_numeric_fusion_val = defaultdict(list)
        self._semantic_categorical_summarization_val = defaultdict(Counter)
        self._points = []
        self._aspects = []
        self._dataset = []
        self._list_rep_point = []

        self.load(path=self._path, ignore_columns=ignore_columns, force_cat_columns=lst_categorical_pd, features=features)

        self._rc = rc
        self._trc = (rc * len(self._points)) if rc > 0.0 else 2

        self.compute_min_spatial_threshold()
        self.summarize_trajectories()


    def reset_values_rt(self):
        self._spatial_cell_grid.clear()
        self._list_rep_point.clear()
        self._representative_trajectory = None
        self._representative_trajectory = MultipleAspectTrajectory('representative')
        if self._daily_info:
            self._representative_trajectory.daily_info = True


    def summarize_trajectories(self):
        temp_max = int(self._aux_max_z)
        temp_better_z = -1
        temp_better_rm = 0
        temp_z_value_rm = 0
        icover_z = -1.0

        info_better_rt = ''
        count = 0

        while temp_max > 1:
            self.reset_values_rt()

            self._cell_size_space = (self._spatial_threshold * int(temp_max)) * 0.7071

            self.allocate_all_points_in_space_cell()

            self.identify_and_process_cells()

            if self._representative_trajectory.point_list:
                temp_z_value_rm = float(self.median_similarity_measure())

                icover_z = self._representative_trajectory.cover_points / len(self._points)

                temp_z_value_rm = (temp_z_value_rm * 0.5) + (icover_z * 0.5)

                if (temp_z_value_rm * 1.1) >= temp_better_rm:
                    temp_better_z = temp_max
                    temp_better_rm = temp_z_value_rm
                    count = 0
                    self._better_rt = copy.deepcopy(self._representative_trajectory)
                    info_better_rt = self.create_info_better_rt(temp_better_z)
                else:
                    count += 1
            temp_max = int(temp_max * 0.85)

            if count > 1:
                break

        if temp_better_z > 1:
            output_file = f"{self._directory}{self._filename} rc {int(self._rc * 100)} rv {int(self._trv * 100)} - z{temp_better_z}.csv"
            print(f"Printing to {output_file}")
            self.write_representative_trajectory(output_file, info_better_rt)

    def create_info_better_rt(self, temp_better_z):
        return (
            f"{temp_better_z}, {self._cell_size_space}, {self._rc}, {self._trv}, "
            f"{len(self._spatial_cell_grid)}, {self._trc}, "
            f"{len(self._better_rt.point_list)}, {self._better_rt.cover_points}, "
            f"{self._spatial_threshold}"
        )
    
    def write_representative_trajectory(self, file_output, info_better_rt:str):
        separator = '###########################'
        with open(file_output, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Method runtime information:'])
            writer.writerow([f"Start timestamp: {self._initial_temp}"])
            writer.writerow([f"End timestamp: {datetime.today()}"])
            writer.writerow(['##'])
            writer.writerow(['Info input dataset:'])
            writer.writerow(['|input.T|', ' |input.T.points|'])
            writer.writerow([str(len(self._dataset)), f" {len(self._points)}"])
            writer.writerow(['##'])
            writer.writerow(['RT setting infos:'])
            writer.writerow(['method', ' thresholdCellSize', ' CellSize', ' tauRelevantCell', ' tauRepresentativenessValue', ' |cell|', ' minPointsRC', ' |rt|', ' |cover_points|', ' spatialThreshold'])
            
            method_name = f"MAT-{self.__class__.__name__[3:]}"
            # Format info_better_rt properly to match the space padding without quotes
            parts = info_better_rt.split(', ')
            writer.writerow([method_name, f" {parts[0]}", f" {parts[1]}", f" {parts[2]}", f" {parts[3]}", f" {parts[4]}", f" {parts[5]}", f" {parts[6]}", f" {parts[7]}", f" {parts[8]}"])
            writer.writerow(['##'])
            writer.writerow(['RT description:'])

            head = ['lat_lon', ' time']
            for att in self._features:
                head.append(' ' + str(att).replace('(', '').replace(',)', '').replace(')', '').lower())
            head.append(' mapping')

            writer.writerow(head)
            for rp in self._better_rt.point_list:
                time_val = str(rp.sti) if rp.sti else "null"
                time_atv = rp.find_feat_value((SemanticAspect("TIME", type=SemanticType.CATEGORICAL),))
                
                if rp.sti is None and time_atv is not None:
                    if isinstance(time_atv[1], dict):
                        time_val = '{' + '; '.join([f"{k}: {v}" for k, v in time_atv[1].items()]) + '}'
                        time_val = time_val.replace("'", "")
                    else:
                        time_val = str(time_atv[1])

                each_point = f"{rp.x} {rp.y}, {time_val}, "

                for att in self._features:
                    atv = rp.find_feat_value(att)
                    if atv is None:
                        each_point += 'null, '
                    else:
                        if isinstance(atv[1], dict):
                            items = []
                            for k, v in atv[1].items():
                                if isinstance(k, tuple):
                                    k_str = "{" + ", ".join(str(i) for i in k) + "}"
                                else:
                                    k_str = str(k)
                                items.append(f"{k_str}: {v}")
                            val_str = '{' + '; '.join(items) + '}'
                        else:
                            val_str = str(atv[1])
                            
                        # Replace to avoid python single quotes and clean up output
                        val_str = val_str.replace("'", "").replace(",", ";")
                        each_point += f"{val_str}, "
                
                each_point += f"{rp.get_mapping_information()}, "

                writer.writerow(each_point.split(','))

    def median_similarity_measure(self):
        if not self._representative_trajectory.point_list:
            print("RT is empty!")
            return -1
        
        measure = MUITAS()

        measure.set_weight('SPATIAL', 0.34)
        measure.set_weight('TIME', 0.33)

        aux_weight = 0.33 / len(self._features)

        for each_feat in self._features:
            measure.set_weight(each_feat, aux_weight)
            for each_att in each_feat:
                if each_att.type == SemanticType.NUMERICAL:
                    measure.set_threshold(each_att, 5)

        measure.set_threshold('SPATIAL', self._spatial_threshold * 2)

        rep_measure = 0
        list_values = [measure.similarity_of(self._representative_trajectory, t) for t in self._dataset]

        rep_measure = np.median(list_values)
        # print(rep_measure)

        return rep_measure
