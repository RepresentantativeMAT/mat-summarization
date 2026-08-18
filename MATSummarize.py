import csv
import copy
from datetime import datetime
import pandas as pd
import numpy as np
from model import *
from model.Util import *
from .MUITAS_V import MUITAS

class MATSummarize:
    def __init__(self, TRC, TRV, path):
        ## Attributes
        self.__consider_nulls = True
        self.__daily_info = False
        self.__rc = 0
        self.__directory = ''
        self.__filename = ''
        self.__path = path
        self.__initial_temp = None
        ## MAT-SG
        self.__trc = TRC
        self.__trv = TRV
        ## Load
        self.__aspects = []
        self.__points = []
        self.__spatial_cell_grid = {}
        self.__points_in_cell = []
        ## Summarization Step
        self.__null_value = 'UNKNOWN'
        self.__representative_trajectory = None
        self.__list_rep_point = []
        self.__present_cell = ''
        self.__list_times_in_cell = []
        self.__semantic_numeric_fusion_val = {}
        self.__semantic_categorical_summarization_val = {}
        self.__avg_x = 0
        self.__avg_y = 0
        ## Spatial Segmentation
        self.__spatial_threshold = 0.0
        self.__cell_size_space = 1.0
        ## AUX
        self.__dataset = []
        self.__better_rt = MultipleAspectTrajectory
        self.__aux_max_z = 0.0

    def load(self, path, ignore_columns = None, force_cat_columns = None):
        always_ignore = ['tid', 'lat_lon', 'time', 'label']
        #   Carrega o Dataset
        df = pd.read_csv(path)

        #   Exclui colunas ignoradas
        if ignore_columns:
            df.drop(columns=ignore_columns, inplace=True, errors='ignore')
        
        #   Analisa e predefine os tipos semanticos das colunas
        order = 0
        for column in df.columns:
            if force_cat_columns and column in force_cat_columns:
                self.__aspects.append(SemanticAspect(column, order, SemanticType.CATEGORICAL))
                
                order += 1
            elif column not in always_ignore:
                self.__aspects.append(SemanticAspect(
                    column,
                    order,
                    SemanticType.CATEGORICAL if not pd.api.types.is_numeric_dtype(df[column]) else SemanticType.NUMERICAL
                    ))
                
                order += 1
        
        #   Cria os MATs
        for i in df['tid'].unique():
            self.__dataset.append(MultipleAspectTrajectory(None, i))

        #   Cria os Points
        rid = 1
        for row in df.itertuples(index=False):
            #   Separa Lat_Lon para X Y
            lat_lon = str(row.lat_lon).split(' ')
            x = float(lat_lon[0].strip())
            y = float(lat_lon[1].strip())

            #   Lista AttributeValues em Semantics
            semantics = []
            for c, v in zip(df.columns, row):
                if c not in always_ignore:
                    aspc = next((a for a in self.__aspects if a.name == c.strip().upper()))
                    if aspc.type == SemanticType.CATEGORICAL and isinstance(v, (int, float)):
                        v = '*' + str(v)
                    semantics.append(AttributeValue(v, aspc, None))

            p = Point(None, rid, x, y, row.time, None, semantics)
            self.__points.append(p)
            self.__dataset[row.tid - 1].addPoint(p)
            rid += 1


    def compute_min_spatial_threshold(self):
        max_distance_to_zero = 0
        aux_value_z = None

        min_distance = float('inf')
        sum_distance = 0
        valid_distances = []

        for p in self.__points:
            aux_value_z = calc_euclidian_dist(p)
            if (aux_value_z > max_distance_to_zero):
                max_distance_to_zero = aux_value_z

            for q in self.__points:
                if not p == q:
                    local_distance = calc_euclidian_dist(p, q)
                    if (local_distance < min_distance):
                        min_distance = local_distance
            
            valid_distances.append(min_distance)
            min_distance = float('inf')

        if(len(valid_distances) > 1):
            median_min_dist = np.median(valid_distances)
            sd_min_dist = np.std(valid_distances)

            less_value_min_dist = median_min_dist - 4 * sd_min_dist
            upper_value_min_dist = median_min_dist + 4 * sd_min_dist

            valid_distances_without_outliers = []
            for dist in valid_distances:
                if (dist >= less_value_min_dist and dist <= upper_value_min_dist and not dist == 0.0):
                    valid_distances_without_outliers.append(dist)
                
            self.__spatial_threshold = np.mean(valid_distances_without_outliers)
            self.__aux_max_z = max_distance_to_zero / self.__spatial_threshold


    def get_cell_position(self, x, y):
        return str(math.floor(x / self.__cell_size_space)) + ', ' + str(math.floor(y / self.__cell_size_space))
    

    def allocate_in_space_cell(self, point):
        key = self.get_cell_position(point.x, point.y)
        rids = self.__spatial_cell_grid.get(key)

        if (rids is None):
            rids = []
            rids.append(point.rId)
            self.__spatial_cell_grid[key] = rids
        else:
            rids.append(point.rId)
            self.__spatial_cell_grid[key] = rids


    def allocate_all_points_in_space_cell(self):
        for p in self.__points:
            self.allocate_in_space_cell(p)


    def summarize_temporal_aspect(self, time_in_points):
        stis = []   #Significant Temporal Intervals
        time_in_points.sort()

        differences = self.compute_time_differences(time_in_points)

        threshold_differences = 100
        if (len(differences) > 2):
            median = np.median(differences)
            sd_deviation = np.std(differences)

            lower_value = median - sd_deviation
            upper_value = median + sd_deviation

            valid_differences = remove_outliers(differences, lower_value, upper_value)
            threshold_differences = math.floor(np.mean(valid_differences))
        
        self.create_temporal_intervals(time_in_points, stis, threshold_differences)
        self.asort_temporal_intervals(stis)
        self.create_representative_points(stis)


    def compute_time_differences(self, tip):
        differences = []
        for i in range(1, len(tip)):
            aux_diff = TimetoMinutes(tip[i]) - TimetoMinutes(tip[i-1])
            if (aux_diff > 0):
                differences.append(aux_diff)
        return differences
    
    def create_temporal_intervals(self, tip, stis, threshold):
        count = 1
        current_interval = None

        for i in range(0, len(tip)):
            if (i != len(tip) - 1 and TimetoMinutes(tip[i]) + threshold >= TimetoMinutes(tip[i + 1])):
                if (not current_interval):
                    current_interval = TemporalAspect(tip[i])
                count += 1
            else:
                if (not current_interval):
                    current_interval = TemporalAspect(tip[i])
                else:
                    current_interval.endTime = tip[i]
                stis.append(STI(current_interval, count / len(tip)))
                count = 1
                current_interval = None


    def asort_temporal_intervals(self, stis:list):
        stis.sort(key=lambda sti: sti.proportion, reverse=True)


    def create_representative_points(self, stis):
        for interval in stis:
            if (interval.proportion >= self.__trv):
                representative_point = self.create_centroid_for_sti(interval)

                if (representative_point.pointListSource):
                    representative_point.sti = interval
                    self.__list_rep_point.append(representative_point)


    def create_centroid_for_sti(self, each_sti):
        temp_rep_p = Centroid()
        for point in self.__points_in_cell:
            if (each_sti.interval.isInInterval(point.time.startTime)):
                temp_rep_p.addPoint(point)
        temp_rep_p.cellReference = self.__present_cell
        return temp_rep_p
    
    
    def identify_times_in_cell(self):
        for k, v in self.__spatial_cell_grid.items():
            cell_analyzed = k

            qtd_points = len(self.__spatial_cell_grid[cell_analyzed])
            if (qtd_points >= self.__trc):
                self.reset_values_to_summarization()

                for point_id in sorted(self.__spatial_cell_grid[cell_analyzed]):
                    self.__points_in_cell.append(self.__points[point_id-1])
                    self.__list_times_in_cell.append(self.__points[point_id-1].time.startTime)
                
                self.__present_cell = cell_analyzed
                self.summarize_temporal_aspect(self.__list_times_in_cell)


    def reset_values_to_summarization(self):
        self.__avg_x = 0
        self.__avg_y = 0

        self.__semantic_numeric_fusion_val.clear()
        self.__semantic_categorical_summarization_val.clear()
        self.__present_cell = ''

        self.__list_times_in_cell.clear()
        self.__points_in_cell.clear()


    def compute_centroid(self):
        self.__list_rep_point.sort(reverse=True)

        for rep_point in self.__list_rep_point:
            self.reset_values_to_summarization()

            self.__representative_trajectory.addPoint(rep_point)
            self.__representative_trajectory.incrementValue(len(rep_point.pointListSource))

            for point in rep_point.pointListSource:
                self.__avg_x += point.x
                self.__avg_y += point.y

                val = 0.0
                attr_actual = ''
                values_num_invalid = [-999.0, -1.0]

                for atv in point.list_attr_values:
                    attr_actual = str(atv.attribute.order)

                    try: 
                        val = float(str(atv.value))
                        self.__aspects[self.__aspects.index(atv.attribute)].type = SemanticType.NUMERICAL

                        if (not attr_actual in self.__semantic_numeric_fusion_val.keys()):
                            self.__semantic_numeric_fusion_val[attr_actual] = []
                        
                        if (not val in values_num_invalid):
                            self.__semantic_numeric_fusion_val[attr_actual].append(val)
                    except ValueError:
                        if (atv.attribute.type is None or not atv.attribute.type == SemanticType.NUMERICAL):
                            self.__aspects[self.__aspects.index(atv.attribute)].type = SemanticType.CATEGORICAL

                            if (not atv.attribute in self.__semantic_categorical_summarization_val.keys()):
                                self.__semantic_categorical_summarization_val[atv.attribute] = {}

                            if (not atv.value in self.__semantic_categorical_summarization_val[atv.attribute]):
                                self.__semantic_categorical_summarization_val[atv.attribute] = {atv.value: 1}
                            else:
                                self.__semantic_categorical_summarization_val[atv.attribute][atv.value] += 1

            rep_point.x = self.__avg_x / len(rep_point.pointListSource)
            rep_point.y = self.__avg_y / len(rep_point.pointListSource)

            for k, v in self.__semantic_numeric_fusion_val.items():
                median = -999.0
                new_map = {}

                if (self.__consider_nulls):
                    if (len(rep_point.pointListSource) - len(v) == len(v)):
                        new_map['-999.0'] = 0.5
                        v.sort()

                        if (len(v) % 2 == 0):
                            median = (v[int(len(v) / 2)] + v[int(len(v) / 2) - 1]) / 2
                        else:
                            median = v[int(len(v) / 2)]
                        new_map[str(median)] = 0.5
                    elif (len(rep_point.pointListSource) - len(v) < len(v)):
                        v.sort()

                        if (len(v) % 2 == 0):
                            median = (v[int(len(v) / 2)] + v[int(len(v) / 2 - 1)]) / 2
                        else:
                            median = v[int(len(v) / 2)]
                else:
                    if (v):
                        if (len(v) % 2 == 0):
                            median = (v[int(len(v) / 2)] + v[int(len(v) / 2 - 1)]) / 2
                        else:
                            median = v[int(len(v) / 2)]
                
                if (not new_map):
                    rep_point.addAttrValue(median, self.__aspects[int(k)])
                else:
                    rep_point.addAttrValue(new_map, self.__aspects[int(k)])

            for k, im in self.__semantic_categorical_summarization_val.items():
                internal_categorical_list = dict(sorted(im.items(), key=lambda item: item[1], reverse=True))
                if (self.__consider_nulls):
                    rep_point.addAttrValue(
                        self.normalize_ranking_values(internal_categorical_list, len(rep_point.pointListSource), 's'),
                        k
                        )
                else:
                    rep_point.addAttrValue(
                        self.normalize_ranking_values_not_nulls(internal_categorical_list, len(rep_point.pointListSource), 's'),
                        k
                        )
                    
        self.reset_values_to_summarization()

    
    def normalize_ranking_values(self, map_rank, size_rp, dimension):
        if (not map_rank):
            raise ValueError("Invalid input: map_rank must not be null or empty.")
        if (size_rp <= 0):
            raise ValueError("Invalid input: size_rp must be a positive value.")
        
        mapped_pts = 0

        for k, v in map_rank.items():
            trend_val = float(v) / size_rp

            if (trend_val >= self.__trv):
                mapped_pts += v
            else:
                map_rank[k] = -1

        new_map = {}

        for k, v in map_rank.items():
            if (v != -1):
                new_map[k] = v / mapped_pts
        
        new_map_sorted = dict(sorted(new_map.items(), key=lambda x: x[1], reverse=True))

        if (dimension[0].lower() == 't'):
            new_time_map = {}

            for k, v in new_map_sorted.items():
                interval = str(k)
                aux_interval = ''

                if ('-' in interval):
                    s, e = interval.split('-')
                    aux_interval = str(MinutestoTime(int(s)))
                    aux_interval += ' - '
                    aux_interval += str(MinutestoTime(int(e)))
                else:
                    aux_interval = str(MinutestoTime(int(interval)))
                
                new_time_map[aux_interval] = new_map[interval]
            return new_time_map
        else:
            return new_map_sorted


    def normalize_ranking_values_not_null(self, map_rank, mapped_pts, dimension):
        if (not map_rank):
            raise ValueError("Invalid input: map_rank must not be null or empty.")
        if (mapped_pts <= 0):
            raise ValueError("Invalid input: mapped_pts must be a positive value.")
        
        new_map = {}
        trend_val = 0.0
        size_not_null = mapped_pts

        if (self.__null_value in map_rank.keys()):
            size_not_null -= map_rank[self.__null_value]

        if (size_not_null < mapped_pts):
            for k, v in map_rank.items():
                if (not k.lower() == 'unknown'):
                    trend_val = float(v) / size_not_null
                    
                    if (trend_val >= self.__trv):
                        new_map[k] = trend_val
        
        new_map_sorted = dict(sorted(new_map.items(), key=lambda x: x[1], reverse=True))

        if (dimension[0].lower() == 't'):
            new_time_map = {}

            for k, v in new_map_sorted.items():
                interval = str(k)
                aux_interval = ''

                if ('-' in interval):
                    s, e = interval.split('-')
                    aux_interval = str(MinutestoTime(int(s)))
                    aux_interval += ' - '
                    aux_interval += str(MinutestoTime(int(e)))
                else:
                    aux_interval = str(MinutestoTime(int(interval)))
                
                new_time_map[aux_interval] = new_map[interval]
            return new_time_map
        else:
            return new_map_sorted
        

    def execute(self, dir, file, lst_categorical_pd, values_null, ignore_columns, pattern_date_input, rc, trv):
        self.__initial_temp = datetime.today()
        self.__directory = dir
        self.__filename = file
        self.__trv = trv
        self.__representative_trajectory = MultipleAspectTrajectory('representative')

        if (pattern_date_input == '?'):
            self.__representative_trajectory.dailyInfo = True
            self.__daily_info = True

        self.__list_times_in_cell = []
        self.__spatial_cell_grid = {}
        self.__semantic_numeric_fusion_val = {}
        self.__semantic_categorical_summarization_val = {}
        self.__points = []
        self.__aspects = []
        self.__dataset = []
        self.__points_in_cell = []
        self.__list_rep_point = []

        self.load(path=self.__path, ignore_columns=ignore_columns, force_cat_columns=lst_categorical_pd)

        self.__rc = rc
        self.__trc = (rc * len(self.__points)) if rc > 0.0 else 2

        self.compute_min_spatial_threshold()
        self.summarize_trajectories()


    def reset_values_rt(self):
        self.__spatial_cell_grid.clear()
        self.__points_in_cell.clear()
        self.__present_cell = None
        self.__list_times_in_cell.clear()
        self.__list_rep_point.clear()
        self.__representative_trajectory = None
        self.__representative_trajectory = MultipleAspectTrajectory('representative')
        if (self.__daily_info):
            self.__representative_trajectory.dailyInfo = True


    def summarize_trajectories(self):
        temp_max = int(self.__aux_max_z)
        temp_better_z = -1
        temp_better_rm = 0
        temp_z_value_rm = 0
        icover_z = -1.0
        temp_only_rm = None

        info_better_rt = ''
        count = 0

        while (temp_max > 1):
            self.reset_values_rt()

            self.__cell_size_space = (self.__spatial_threshold * int(temp_max)) * 0.7071

            self.allocate_all_points_in_space_cell()

            self.identify_times_in_cell()

            self.compute_centroid()

            if (self.__representative_trajectory.pointList):
                temp_z_value_rm = float(self.median_similarity_measure())
                temp_only_rm = temp_z_value_rm

                icover_z = self.__representative_trajectory.coverPoints / len(self.__points)

                temp_z_value_rm = (temp_z_value_rm * 0.5) + (icover_z * 0.5)

                if ((temp_z_value_rm * 1.1) >= temp_better_rm):
                    temp_better_z = temp_max
                    temp_better_rm = temp_z_value_rm
                    count = 0
                    self.__better_rt = copy.deepcopy(self.__representative_trajectory)
                    info_better_rt = self.create_info_better_rt(temp_better_z)
                else:
                    count += 1
            temp_max = int(temp_max * 0.85)

            if (count > 1):
                break

        if (temp_better_z > 1):
            outputFile = self.__directory + self.__filename + " rc " + str(int(self.__rc * 100)) + " rv " + str(int(self.__trv * 100)) + " - z" + str(temp_better_z) + '.csv'
            print('Printing to', outputFile)
            self.write_representative_trajectory(outputFile, info_better_rt)


    def create_info_better_rt(self, temp_better_z):
        return (
            str(temp_better_z) + ', '
            + str(self.__cell_size_space) + ', '
            + str(self.__rc) + ', '
            + str(self.__trv) + ', '
            + str(len(self.__spatial_cell_grid)) + ', '
            + str(self.__trc) + ', '
            + str(len(self.__better_rt.pointList)) + ', '
            + str(self.__better_rt.coverPoints)
            )
    

    def write_representative_trajectory(self, file_output, info_better_rt:str):
        separator = '###########################'
        with open(file_output, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Method runtime information:'])
            writer.writerow(['Start timestamp: ' + str(self.__initial_temp)])
            writer.writerow(['End timestamp: ' + str(datetime.today())])
            writer.writerow([separator])
            writer.writerow(['Info input dataset:'])
            writer.writerow(['input.T', 'input.T.points'])
            writer.writerow([str(len(self.__dataset)), str(len(self.__points))])
            writer.writerow([separator])
            writer.writerow(['RT setting infos:'])

            writer.writerow([
                'thresholdCellSize',
                'cellSize',
                'tauRelevantCell',
                'tauRepresentativenessValue',
                'cell', 'minPointsRC',
                'rt', 'coverPoints'
                ])
            
            writer.writerow(info_better_rt.split(','))
            writer.writerow([separator])
            writer.writerow(['RT description:'])

            head = ['lat_lon', 'time']
            for att in self.__aspects:
                head.append(att.name.lower())
            head.append('mapping')

            writer.writerow(head)
            for rp in self.__better_rt.pointList:
                each_point = str(rp.x) + ' ' + str(rp.y) + ', '
                each_point += str(rp.sti) + ', '

                for att in self.__aspects:
                    atv = rp.findAttributeValue(att.name)
                    each_point += 'null, ' if atv is None else (str(atv.value).replace(',', ';').replace('=', ':').replace('*', '') + ', ')
                
                each_point += str(rp.getMappingInformation()) + ', '

                writer.writerow(each_point.split(','))

    
    def median_similarity_measure(self):
        if (not self.__representative_trajectory.pointList):
            print("RT is empty!")
            return -1
        
        measure = MUITAS()

        measure.set_weight('SPATIAL', 0.34)
        measure.set_weight('TIME', 0.33)

        aux_weight = 0.33 / len(self.__aspects)

        for each_att in self.__aspects:
            measure.set_weight(each_att, aux_weight)
            if (each_att.type == SemanticType.NUMERICAL):
                measure.set_threshold(each_att, 10)

        measure.set_threshold('SPATIAL', self.__spatial_threshold * 2)

        rep_measure = 0
        list_values = []

        for each_traj in self.__dataset:
            list_values.append(measure.similarity_of(self.__representative_trajectory, each_traj))

        rep_measure = np.median(list_values)

        return rep_measure