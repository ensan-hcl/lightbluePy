from cat import Cat
from enum import Enum
from dataclasses import dataclass


class RuleSymbol(Enum):
    """The name of the CCG rule to derive the node."""

    LEX = 0
    """A lexical item"""

    EC = 1
    """An empty category"""
    FFA = 2
    """Forward function application rule."""
    BFA = 3
    """Backward function application rule"""
    FFC1 = 4
    """Forward function composition rule 1"""
    BFC1 = 5
    """Backward function composition rule 1"""
    FFC2 = 6
    """Forward function composition rule 2"""
    BFC2 = 7
    """Backward function composition rule 2"""
    FFC3 = 8
    """Forward function composition rule 3"""
    BFC3 = 9
    """Backward function composition rule 3"""
    FFCx1 = 10
    """Forward function crossed composition rule 1"""
    FFCx2 = 11
    """Forward function crossed composition rule 2"""
    FFSx = 12
    """Forward function crossed substitution rule"""
    COORD = 13
    """Coordination rule"""
    PAREN = 14
    """Parenthesis rule"""
    WRAP = 15
    """Wrap rule"""
    DC = 16
    """Dynamic conjunction rule"""
    DREL = 17
    """Discourse Relation rule"""

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


@dataclass
class Node:
    rs: RuleSymbol
    pf: str
    cat: Cat
    # sem: Preterm
    # sig: Signature
    daughters: list["Node"]
    score: float
    source: str

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Node):
            return False
        return self.rs == __value.rs and self.pf == __value.pf and self.cat == __value.cat and self.daughters == __value.daughters and self.score == __value.score and self.source == __value.source
