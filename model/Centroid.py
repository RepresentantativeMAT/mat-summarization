from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .STI import STI
    from .Centroid import Centroid

from .Point import Point

class Centroid(Point):
##  Construtor  ##
    def __init__(self, x:float|None = None, y:float|None = None, point:Point|None = None):
        self.__sti = None
        if (x is None and y is None and point is None):
            super().__init__()
            self.__point_list_source = []
            self.__list_sti = []
        elif (x is None and y is None and point is not None):
            super().__init__(x=point.x, y=point.y, semantics=point.list_attr_values)
            self.__point_list_source = []
            self.__list_sti = []
        else:
            super().__init__(x=x, y=y, semantics=point.list_attr_values)
            self.__point_list_source = []
            self.__list_sti = []


##  Getters and Setters  ##
    #   STI
    @property
    def sti(self) -> (STI|None):
        return self.__sti
    
    @sti.setter
    def sti(self, sti:STI):
        self.__sti = sti
        if (sti is not None):
            self.sti.point = self

    #   PointListSource
    @property
    def point_list_source(self) -> list[Point]:
        return self.__point_list_source
    
    #   ListSTI
    @property
    def list_sti(self) -> list[STI]:
        return self.__list_sti


##  Functions  ##
    def add_point(self, point:Point):
        self.__point_list_source.append(point)

        
    def get_mapping_information(self) -> str:
        txt = '{'
        for i, p in enumerate(self.point_list_source):
            txt += str(p.trajectory.id) + ': ' + str(p.rid)
            if i < len(self.point_list_source) - 1:
                txt += '; '
        txt += '}'
        return txt
    
    def show_attr_values(self) -> str:
        txt = ''
        for atv in self.list_attr_values:
            txt += '\n'

            if (not isinstance(atv.value, dict)):
                txt += str(atv.attribute.name) + '= ' + str(atv.value)
            else:
                txt += 'Ranking of ' + atv.attribute.name + '= ['
                all_values = atv.value
                for key, value in all_values.items():
                    txt += key.replace(",", ";") + " -> " + "{:.2f}".format(value) + ", "
                txt += ' ], '

        if (self.list_sti):
            txt += 'Ranking of Temporal Interval = ['
            for sti in self.list_sti:
                txt += str(sti) + ', '
            txt += '], '
        
        return txt


##  Hash  ##
    def __hash__(self) -> int:
        h = 7
        h = 17 * h + hash(self.__point_list_source)
        h = 17 * h + hash(self.__list_sti)
        return h


##  Equals  ##
    def equals(self, other) -> bool:
        if (self is other):
            return True
        if (other is None):
            return False
        if (type(self) != type(other)):
            return False
        if (self.list_sti != other.list_sti):
            return False
        return True
    
    def __eq__(self, other) -> bool:
        return self.equals(other)
    

## Less Than ##
    def __lt__(self, other:Centroid) -> bool:
        if self.sti and other.sti:
            return self.sti.interval.start_time > other.sti.interval.start_time
        
        self_time = min([p.time.start_time for p in self.point_list_source]) if self.point_list_source else 0
        other_time = min([p.time.start_time for p in other.point_list_source]) if other.point_list_source else 0
        return self_time > other_time


##  ToString  ##
    def __str__(self) -> str:
        txt = 'rt'
        txt += '\n(x,y)= (' + f"{self.x:.2f}" + ',' + f"{self.y:.2f}" + ')'
        if (self.list_attr_values):
            txt += self.show_attr_values()
        if (self.sti):
            txt += '\nTime: ' + str(self.sti)
        txt += '\nCell: ' + self.cell_reference + '\nLocal mapped: '
        for p in self.point_list_source:
            txt += str(p.trajectory.id) + ' - ' + str(p.rid) + ', '
        return txt