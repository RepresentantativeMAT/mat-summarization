from model import MultipleAspectTrajectory, STI, Centroid, Point, SemanticAspect
from model import Util

class MUITAS:
    def __init__(self):
        self.__weights: dict[object, float] = {}
        self.__thresholds: dict[object, float] = {}
        self.__parity_T1T2: float = 0.0
        self.__parity_T2T1: float = 0.0

    
    @property
    def parity_t1_t2(self):
        return self.__parity_T1T2
    
    @property
    def parity_t2_t1(self):
        return self.__parity_T2T1


    def clear(self):
        self.__weights.clear()
        self.__thresholds.clear()


    def set_threshold(self, att: object, threshold: float):
        self.__thresholds[att] = threshold


    def get_threshold(self, att: object) -> float:
        if (not self.__thresholds):
            raise ValueError('Threshold list is empty')
        
        try:
            if (att in self.__thresholds.keys()):
                return self.__thresholds[att]
            else:
                raise ValueError('Threshold not found for attribute: "', att, '"')
        except:
            raise ValueError('Invalid attribute type')


    def set_weight(self, attribute: object, weight: float):
        self.__weights[attribute] = weight


    def get_weight(self, attribute: object) -> float:
        try:
            if isinstance(attribute, STI):
                return self.__weights['TIME']
            else:
                return self.__weights[attribute]
        except:
            print('Error in get_weight for"', attribute, '" (weights:', self.__weights, ')')
            raise
    

    def similarity_of(self, t1: MultipleAspectTrajectory, t2: MultipleAspectTrajectory) -> float:
        self.__parity_T1T2 = 0
        self.__parity_T2T1 = 0
        scores = []

        for i in range(len(t1.point_list)):
            scores.append([])
            max_score_row = 0

            for j in range(len(t2.point_list)):
                scores[i].append([])
                
                scores[i][j] = self.score(t1.point_list[i], t2.point_list[j])
                max_score_row = scores [i][j] if scores[i][j] > max_score_row else max_score_row

            self.__parity_T1T2 += max_score_row

        for j in range(len(t2.point_list)):
            max_col = 0

            for i in range(len(t1.point_list)):
                max_col = scores[i][j] if scores[i][j] > max_col else max_col

            self.__parity_T2T1 += max_col
        return (self.__parity_T1T2 + self.__parity_T2T1) / (len(t1.point_list) + len(t2.point_list))
    

    def score(self, p1: Centroid, p2: Point) -> float:
        score = 0

        if (Util.calc_euclidian_dist(p1, p2) <= self.get_threshold('SPATIAL')):
            score += self.get_weight('SPATIAL')
        
        s_match = 1 if p1.sti and p1.sti.interval.is_in_interval(p2.time.start_time) else 0
        score += s_match * self.get_weight('TIME')

        for atv_p1 in p1.list_feat_values.items():
            temp_att_p2 = p2.find_feat_value(atv_p1) if atv_p1 is not None else None

            temp_semantic_match = self.compute_match(atv_p1, temp_att_p2)
            score += temp_semantic_match

        return score
    

    def compute_match(self, rep: tuple[tuple[SemanticAspect, ...], list[object]], atv: tuple[tuple[SemanticAspect, ...], list[object]]) -> float:
        c_match = 0

        if (atv is None or rep is None):
            return 0

        if (isinstance(rep[1], dict)):
            values_rt = rep[1]
            if (str(atv[1]) in values_rt):
                c_match = 1
        else:
            try:
                c_match = 1 if abs(float(str(rep[1])) - float(str(atv[1]))) <= self.get_threshold(atv[0]) else 0
            except AttributeError:
                c_match = 1 if abs(float(str(rep[1])) - float(str(atv[1]))) <= 1 else 0
            except TypeError:
                c_match = 1 if atv[1] == rep[1] else 0

        return c_match * self.get_weight(rep[0])