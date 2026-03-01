from .SemanticType import SemanticType

class SemanticAspect:
##  Construtor  ##
    def __init__(self, name:str, order:int = None, type:SemanticType = None):
        self.__name:str = name.strip().upper()
        self.__order:int = order
        self.__type:SemanticType = type


## Getters and Setters  ##
    #   Name
    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, name:str):
        self.__name = name

    #   Order
    @property
    def order(self) -> int:
        return self.__order
    
    @order.setter
    def order(self, order:int):
        self.__order = order

    #   Type
    @property
    def type(self) -> SemanticType:
        return self.__type
    
    @type.setter
    def type(self, type:SemanticType):
        self.__type = type


##  Hash  ##
    def __hash__(self) -> int:
        h = 3
        h = 67 * h + hash(self.__name)
        return h
    

##  Equals  ##
    def equals(self, other) -> bool:
        if (self is other):
            return True
        if (other is None):
            return False
        if (type(self) != type(other)):
            return False
        if (self.name.upper() != other.name.upper()):
            return False
        return True
    
    def __eq__(self, other) -> bool:
        return self.equals(other)
    

##  ToString  ##
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) ->str:
        return 'SemanticAspect(' + self.name + ', ' + str(self.order) + ', ' + str(self.type.description) + ')'