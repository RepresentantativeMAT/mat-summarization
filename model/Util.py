from datetime import time
import struct
import math

def minutes_to_time(minutes:int) -> time:
    return time(hour=(minutes // 60), minute=(minutes % 60))

def time_to_minutes(time:time) -> int:
    return time.hour * 60 + time.minute

def FloatToIntBits(float:float):
    return struct.unpack('!I', struct.pack('!f', float))[0]

def float_to_long_bits(float:float):
    long_bits = struct.unpack('!Q', struct.pack('!d', float))[0]
    bits = long_bits ^ (long_bits >> 32)
    return bits & 0xFFFFFFFF

def calc_euclidian_dist(point1, point2 = None) -> float:
    if point2 is not None:
        return math.sqrt(math.pow(point1.x - point2.x, 2) + math.pow(point1.y - point2.y, 2))
    else:
        return math.sqrt(math.pow(point1.x, 2) + math.pow(point1.y, 2))
    
def remove_outliers(values, lower_value, upper_value) -> list:
    valid_values = []
    for val in values:
        if (val >= lower_value and val <= upper_value):
            valid_values.append(val)
    return valid_values