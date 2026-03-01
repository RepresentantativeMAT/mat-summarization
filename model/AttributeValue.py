from .SemanticAspect import SemanticAspect

class AttributeValue:
##   Construtor  ##
    def __init__(self, value:object, attribute:SemanticAspect, numerical_value_sd:float|None = None):
        self.__value:object = value
        self.__attribute:SemanticAspect = attribute
        self.__numerical_value_sd:float = numerical_value_sd


##  Getters and Setters  ##
    #   Value   #
    @property
    def value(self) -> object:
        return self.__value
    
    @value.setter
    def value(self, value:object):
        self.__value = value
    
    #   Attribute   #
    @property
    def attribute(self) -> SemanticAspect:
        return self.__attribute
    
    @attribute.setter
    def attribute(self, attribute:SemanticAspect):
        self.__attribute = attribute

    #   Numerical_value_sd    #
    @property
    def numerical_value_sd(self) -> float:
        return self.__numerical_value_sd
    
    @numerical_value_sd.setter
    def numerical_value_sd(self, numerical_value_sd:float):
        self.__numerical_value_sd = numerical_value_sd


##  Hash  ##
    def __hash__(self) -> int:
        h = 5
        h = 79 * h + hash(self.value)
        h = 79 * h + hash(self.attribute)
        return h
    

##  Equals  ##
    def equals(self, other) -> bool:
        if (self is other):
            return True
        if (other is None):
            return False
        if (type(self) != type(other)):
            return False
        if (self.value != other.value):
            return False
        if (self.attribute != other.attribute):
            return False
        return True
    
    def __eq__(self, other):
        return self.equals(other)
    

##  ToString  ##
    def __str__(self) -> str:
        return self.attribute.name + ': ' + str(self.value)
    
    def __repr__(self) -> str:
        return 'AttributeValue(' + str(self.value) + ', (' + str(self.attribute) + ', ' + str(self.attribute.type.description) + ', ' + str(self.numerical_value_sd) + ')'