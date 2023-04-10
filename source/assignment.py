from dataclasses import dataclass
from typing import TypeAlias, Union, TypeVar, Generic

@dataclass
class SubstLink:
    index: int


T1 = TypeVar("T1")
T2 = TypeVar("T2")


@dataclass
class SubstVal(Generic[T1]):
    value: T1


SubstData: TypeAlias = Union[SubstLink, SubstVal[T1]]
Assignment: TypeAlias = list[tuple[int, SubstData]]
