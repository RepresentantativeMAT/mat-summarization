from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .TemporalAspect import TemporalAspect
    from .Point import Point

from datetime import time
from .Util import FloatToIntBits, float_to_long_bits

class STI:
##  Construtor  ##
    def __init__(self, interval:TemporalAspect = None, proportion:float = None, point:Point = None, start_time:time|None = None, end_time:time|None = None):
        if interval is not None and start_time is None:
            self.__interval = interval
            self.__proportion = proportion
            self.__point = point
        elif interval is None and start_time is not None:
            self.__interval = TemporalAspect(start_time, end_time)
            self.__proportion = proportion
            self.__point = point
        else:
            raise ValueError('Invalid Constructor Arguments')
        

##  Getters and Setters  ##
    #   Interval
    @property
    def interval(self) -> TemporalAspect:
        return self.__interval
    
    @interval.setter
    def interval(self, interval:TemporalAspect):
        self.__interval = interval

    #   Proportion
    @property
    def proportion(self) -> float:
        return self.__proportion
    
    @proportion.setter
    def proportion(self, proportion:float):
        self.__proportion = proportion

    #   Point
    @property
    def point(self) -> Point:
        return self.__point
    
    @point.setter
    def point(self, point:Point):
        self.__point = point


##  Hash  ##
    def __hash__(self) -> int:
        h = 7
        h = 97 * h + hash(self.interval)
        h = 97 * h + FloatToIntBits(self.proportion)
        return h


##  Equals  ##
    def equals(self, other) -> bool:
        if (self is other):
            return True
        if (other is None):
            return False
        if (type(self) != type(other)):
            return False
        if (FloatToIntBits(self.proportion) != FloatToIntBits(other.proportion)):
            return False
        if (self.interval != other.interval):
            return False
        return True
    
    def __eq__(self, other) -> bool:
        return self.equals(other)


##  ToString  ##
    def __str__(self) -> str:
        return str(self.interval)