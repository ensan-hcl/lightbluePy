from dataclasses import dataclass
from typing import TypeAlias, Union
from enum import Enum


class FeatureValue(Enum):
    """Values of syntactic features of Japanese"""
    V5k = 0
    V5s = 1
    V5t = 2
    V5n = 3
    V5m = 4
    V5r = 5
    V5w = 6
    V5g = 7
    V5z = 8
    V5b = 9
    V5IKU = 10
    V5YUK = 11
    V5ARU = 12
    V5NAS = 13
    V5TOW = 14
    V1 = 15
    VK = 16
    VS = 17
    VSN = 18
    VZ = 19
    VURU = 20
    Aauo = 21
    Ai = 22
    ANAS = 23
    ATII = 24
    ABES = 25
    Nda = 26
    Nna = 27
    Nno = 28
    Ntar = 29
    Nni = 30
    Nemp = 31
    Nto = 32
    Exp = 33
    Stem = 34
    UStem = 35
    NStem = 36
    Neg = 37
    Cont = 38
    Term = 39
    Attr = 40
    Hyp = 41
    Imper = 42
    Pre = 43
    NTerm = 44
    NegL = 45
    TeForm = 46
    NiForm = 47
    EuphT = 48
    EuphD = 49
    ModU = 50
    ModD = 51
    ModS = 52
    ModM = 53
    VoR = 54
    VoS = 55
    VoE = 56
    P = 57
    M = 58
    Nc = 59
    Ga = 60
    O = 61
    Ni = 62
    To = 63
    Niyotte = 64
    No = 65
    ToCL = 66
    YooniCL = 67
    Decl = 68


@dataclass
class F:
    """Syntactic feature"""
    features: list[FeatureValue]


@dataclass
class SF:
    """Shared syntactic feature (with an index)"""
    index: int
    features: list[FeatureValue]


Feature: TypeAlias = Union[F, SF]
