from dataclasses import dataclass
from typing import TypeAlias, Union
from enum import Enum, auto


class FeatureValue(Enum):
    """Values of syntactic features of Japanese"""
    V5k = auto()
    V5s = auto()
    V5t = auto()
    V5n = auto()
    V5m = auto()
    V5r = auto()
    V5w = auto()
    V5g = auto()
    V5z = auto()
    V5b = auto()
    V5IKU = auto()
    V5YUK = auto()
    V5ARU = auto()
    V5NAS = auto()
    V5TOW = auto()
    V1 = auto()
    VK = auto()
    VS = auto()
    VSN = auto()
    VZ = auto()
    VURU = auto()
    Aauo = auto()
    Ai = auto()
    ANAS = auto()
    ATII = auto()
    ABES = auto()
    Nda = auto()
    Nna = auto()
    Nno = auto()
    Ntar = auto()
    Nni = auto()
    Nemp = auto()
    Nto = auto()
    Exp = auto()
    Stem = auto()
    UStem = auto()
    NStem = auto()
    Neg = auto()
    Cont = auto()
    Term = auto()
    Attr = auto()
    Hyp = auto()
    Imper = auto()
    Pre = auto()
    NTerm = auto()
    NegL = auto()
    TeForm = auto()
    NiForm = auto()
    EuphT = auto()
    EuphD = auto()
    ModU = auto()
    ModD = auto()
    ModS = auto()
    ModM = auto()
    VoR = auto()
    VoS = auto()
    VoE = auto()
    P = auto()
    M = auto()
    Nc = auto()
    Ga = auto()
    O = auto()
    Ni = auto()
    To = auto()
    Niyotte = auto()
    No = auto()
    ToCL = auto()
    YooniCL = auto()
    Decl = auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


@dataclass
class F:
    """Syntactic feature"""
    features: list[FeatureValue]

    def __str__(self):
        return f"F({self.features})"

    def __repr__(self):
        return self.__str__()


@dataclass
class SF:
    """Shared syntactic feature (with an index)"""
    index: int
    features: list[FeatureValue]

    def __str__(self):
        return f"SF({self.index}, {self.features})"

    def __repr__(self):
        return self.__str__()


Feature: TypeAlias = Union[F, SF]
