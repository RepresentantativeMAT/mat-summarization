from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Point import Point

class MultipleAspectTrajectory:
##  Construtor  ##
    def __init__(self, description:str|None = None, id:int|None = None):
        self.__description = description if description else ''
        self.__id = id
        self.__point_list = []
        self.__cover_points = 0
        self.__daily_info = False


##  Getters and Setters  ##
    #   Description
    @property
    def description(self) -> str:
        return self.__description
    
    @description.setter
    def description(self, description:str):
        self.__description = description

    #   Id
    @property
    def id(self) -> int:
        return self.__id
    
    @id.setter
    def id(self, id:int):
        self.__id = id

    #   CoverPoints
    @property
    def cover_points(self) -> int:
        return self.__cover_points
    
    @cover_points.setter
    def cover_points(self, cover_points:int):
        self.__cover_points = cover_points

    #   PointList
    @property
    def point_list(self) -> list[Point]:
        return self.__point_list
    
    #   DailyInfo
    @property
    def daily_info(self) -> bool:
        return self.__daily_info
    
    @daily_info.setter
    def daily_info(self, daily_info:bool):
        self.__daily_info = daily_info

##  Functions  ##
    def add_point(self, point:Point):
        self.point_list.append(point)
        point.trajectory = self
    
    def increment_value(self, sizeDataPoints:int):
        self.cover_points += sizeDataPoints


##  Hash  ##
    def __hash__(self) -> int:
        h = 3
        h = 97 * h + self.id
        return h
    

##  Equals  ##
    def equals(self, other) -> bool:
        if (self is other):
            return True
        if (other is None):
            return False
        if (type(self) != type(other)):
            return False
        return self.id == other.id
    
    def __eq__(self, other) -> bool:
        return self.equals(other)


##  ToString  ##
    def __str__(self) -> str:
        aux = 'ID: ' + str(id)
        aux += '\nDescription: ' + self.description
        if (self.point_list):
            aux += '\nPoint List:\n'

            for point in self.point_list:
                aux += str(point) + '\n'
        return aux
    
    def __repr__(self) -> str:
        return 'MAT <' + str(self.__id) + '>'
