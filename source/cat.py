from dataclasses import dataclass
from typing import TypeAlias, Union, TypeVar, Generic

from feature import Feature


@dataclass
class S:
    features: list[Feature]


@dataclass
class NP:
    features: list[Feature]


@dataclass
class N:
    pass


@dataclass
class Sbar:
    features: list[Feature]


@dataclass
class CONJ:
    pass


@dataclass
class LPAREN:
    pass


@dataclass
class RPAREN:
    pass


@dataclass
class SL:
    left: "Cat"
    right: "Cat"


@dataclass
class BS:
    left: "Cat"
    right: "Cat"


@dataclass
class T:
    is_closed: bool
    index: int
    restriction: "Cat"


Cat: TypeAlias = Union[S, NP, N, Sbar,
                       CONJ, LPAREN, RPAREN, SL, BS, T]
