from datetime import time, datetime
from model import Point, Centroid

point = Point(x=1, y=1, start_time=1)
centroid = Centroid(x=1, y=1, point=point)
print('Point----------------------------')
print(point)
print('Centroid-------------------------')
print(centroid)