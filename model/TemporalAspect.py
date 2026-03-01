from datetime import time
from .Util import minutes_to_time, time_to_minutes

class TemporalAspect:
##  Construtor  ##
    def __init__(self, start_time:time|int = None, end_time:time|None = None):
        if isinstance(start_time, int):
            start_time = minutes_to_time(start_time)
            end_time = None
            self.__daily_info = True
        self.__start_time = start_time
        self.__end_time = end_time


##  Getters and Setters  ##
    #   StartTime
    @property
    def start_time(self) -> time:
        return self.__start_time
    
    @start_time.setter
    def start_time(self, start_time:time|int):
        if isinstance(start_time, int):
            start_time = minutes_to_time(start_time)
        self.__start_time = start_time

    #   EndTime
    @property
    def end_time(self) -> time:
        return self.__end_time
    
    @end_time.setter
    def end_time(self, end_time:time|int):
        if isinstance(end_time, int):
            end_time = minutes_to_time(end_time)
        self.__end_time = end_time

    #   DailyInfo
    @property
    def daily_info(self) -> bool:
        return self.__daily_info
    
    @daily_info.setter
    def daily_info(self, daily_info:bool):
        self.__daily_info = daily_info


##  Functions  ##
    def is_in_interval(self, time:time) -> bool:
        return ((self.start_time <= time and (self.end_time is None or self.end_time >= time)) or (self.start_time == time) or (self.end_time == time))


##  Hash  ##
    def __hash__(self) -> int:
        h = 7
        h = 29 * h + hash(self.start_time)
        h = 29 * h + hash(self.end_time)
        return h


##  Equals  ##
    def equals(self, other) -> bool:
        if (self is other):
            return True
        if (other is None):
            return False
        if (type(self) != type(other)):
            return False
        if (self.start_time != other.start_time):
            return False
        if (self.end_time != other.end_time):
            return False
        return True
    
    def __eq__(self, other) -> bool:
        return self.equals(other)


##  ToString  ##
    def __str__(self) -> str:
        return self.start_time.strftime('%H:%M') + ((' - ' + self.end_time.strftime('%H:%M')) if self.end_time else '')