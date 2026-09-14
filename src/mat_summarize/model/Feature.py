from typing import List, Tuple
from .Point import Point

class Feature:
    def __init__(self, name: str, attributes: List[str]):
        """
        Creates a new composite feature based on semantic attributes.
        :param name: The composite feature name (e.g., 'POI_PRICE')
        :param attributes: List of attribute names to combine (e.g., ['POI', 'price'])
        """
        self.name = name
        self.attributes = attributes

    def extract_from_point(self, point: Point) -> Tuple[str, ...]:
        """
        Extracts the values of the configured attributes from a point, 
        returning them as a tuple. If any attribute is missing, returns 'UNKNOWN'.
        """
        extracted_values = []
        for attr_name in self.attributes:
            atv = point.find_attribute_value(attr_name)
            if atv is not None and atv.value is not None:
                extracted_values.append(str(atv.value))
            else:
                extracted_values.append("UNKNOWN")
        return tuple(extracted_values)
