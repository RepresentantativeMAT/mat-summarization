from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .MultipleAspectTrajectory import MultipleAspectTrajectory
    from .SemanticAspect import SemanticAspect
    from .Point import Point
    import datetime

from .TemporalAspect import TemporalAspect
from .Util import minutes_to_time, float_to_long_bits

class Point:
##  Construtor  ##
    def __init__(self, trajectory:MultipleAspectTrajectory = None, rid:int = None, x:float = None, y:float = None, start_time:datetime.time|int = None, end_time:datetime.time|int = None, semantics:dict[tuple[SemanticAspect, ...], list[object]] = None):
        if isinstance(start_time, int):
            start_time:datetime.time = minutes_to_time(start_time)
        if isinstance(end_time, int):
            end_time:datetime.time = minutes_to_time(end_time)
        self.__trajectory:MultipleAspectTrajectory = trajectory
        self.__rid:int = rid
        self.__x:float = x
        self.__y:float = y
        self.__time:TemporalAspect = TemporalAspect(start_time, end_time)
        self.__list_feat_values:dict[tuple[SemanticAspect, ...], list[object]] = (semantics if semantics else {})
        self.__cell_reference:str = ''


##  Getters and Setters  ##
    #   Trajectory
    @property
    def trajectory(self) -> MultipleAspectTrajectory:
        return self.__trajectory
    
    @trajectory.setter
    def trajectory(self, trajectory:MultipleAspectTrajectory):
        self.__trajectory = trajectory

    #   RId
    @property
    def rid(self) -> int:
        return self.__rid
    
    @rid.setter
    def rid(self, rid:int):
        self.__rid = rid

    #   X
    @property
    def x(self) -> float:
        return self.__x
    
    @x.setter
    def x(self, x:float):
        self.__x = x

    #   Y
    @property
    def y(self) -> float:
        return self.__y
    
    @y.setter
    def y(self, y:float):
        self.__y = y

    #   Time
    @property
    def time(self) -> TemporalAspect:
        return self.__time
    
    @time.setter
    def time(self, start_time:datetime.time|int, end_time:datetime.time|None = None):
        self.__time = TemporalAspect(start_time, end_time)
    
    #   List_attr_values
    @property
    def list_feat_values(self) -> dict[tuple[SemanticAspect, ...], list[object]]:
        return self.__list_feat_values
    
    @list_feat_values.setter
    def list_feat_values(self, list_feat_values:dict[tuple[SemanticAspect, ...], list[object]]):
        self.__list_feat_values = list_feat_values

    #   Cell_reference
    @property
    def cell_reference(self) -> str:
        return self.__cell_reference.replace(',', ' ')
    
    @cell_reference.setter
    def cell_reference(self, cell_reference:str):
        self.__cell_reference = cell_reference


##  Functions  ##
    def add_feat_value(self, value:object, feat:tuple[SemanticAspect, ...]):
        self.list_feat_values[feat] = value

    def show_feat_values(self) -> str:
        return str(self.list_feat_values)
        
    
    def get_feat_value(self, feat:tuple[tuple[SemanticAspect, ...], list[object]]) -> (tuple[tuple[SemanticAspect, ...], list[object]]|None):
        if feat[0] in self.list_feat_values and feat[1] == self.list_feat_values[feat[0]]:
            return (feat[0], self.list_feat_values[feat[0]])
        return None
    
    def find_feat_value(self, feat:tuple[SemanticAspect, ...]) -> (tuple[tuple[SemanticAspect, ...], list[object]]|None):
        if feat in self.list_feat_values:
            return (feat, self.list_feat_values[feat])
        return None


##  Hash  ##

    def __hash__(self) -> int:
        h = 7
        h = 89 * h + hash(self.trajectory)
        h = 89 * h + self.rid
        h = 89 * h + float_to_long_bits(self.x)
        h = 89 * h + float_to_long_bits(self.y)
        h = 89 * h + hash(tuple(self.list_feat_values.items()))
        h = 89 * h + hash(self.time)
        return h



##  Equals  ##
    def equals(self, other) -> bool:
        if (self is other):
            return True
        if (other is None):
            return False
        if (type(self) != type(other)):
            return False
        if (self.x != other.x):
            return False
        if (self.y != other.y):
            return False
        if (self.trajectory != other.trajectory):
            return False
        if (self.list_feat_values != other.list_feat_values):
            return False
        if (self.time != other.time):
            return False
        return True
    
    def __eq__(self, other) -> bool:
        return self.equals(other)
    

##  ToString  ##
    def __str__(self) -> str:
        txt = ('RId: ' + str(self.rid)) if self.rid != 0 else 'RT'
        txt += '\n(x,y)= (' + f"{self.x:.2f}" + ', ' + f"{self.y:.2f}" + ')'
        if (self.time):
            txt += '\nTemporal Aspect: ' + str(self.time)
        if (self.list_attr_values):
            txt += '\n' + self.show_feat_values()
        return txt