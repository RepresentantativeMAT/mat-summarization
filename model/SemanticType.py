from enum import Enum

class SemanticType(Enum):
    CATEGORICAL = 'categorical'
    NUMERICAL = 'numerical'

    def __init__(self, description:str):
        self.__description:str = description

    def __lt__(self, other):
        order = {
            SemanticType.CATEGORICAL: 0,
            SemanticType.NUMERICAL: 1
        }

        if isinstance(other, SemanticType):
            return order[self] < order[other]

        return NotImplemented

    @property
    def description(self) -> str:
        return self.__description