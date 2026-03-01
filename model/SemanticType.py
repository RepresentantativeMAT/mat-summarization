from enum import Enum

class SemanticType(Enum):
    CATEGORICAL = 'categorical'
    NUMERICAL = 'numerical'

    def __init__(self, description:str):
        self.__description:str = description

    @property
    def description(self) -> str:
        return self.__description