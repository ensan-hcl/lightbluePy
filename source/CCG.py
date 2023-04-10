from dataclasses import dataclass
# enum
from enum import Enum
from typing import TypeVar, Optional

import cat
import feature
from cat import Cat
from assignment import SubstData, Assignment, SubstLink, SubstVal
from feature import Feature
from feature import FeatureValue as FV

from leixcon.lexicon import constructPredicate


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


def unifiable(f1: list[Feature], f2: list[Feature]) -> bool:
    """checks if two lists of features are unifiable."""
    return unifyFeatures([], f1, f2) is not None


def isBaseCategory(c: Cat) -> bool:
    """A test to check if a given category is a base category (i.e. not a functional category nor a category variable)."""
    match c:
        case cat.S(_):
            return True
        case cat.NP(_):
            return True
        case cat.T(False, _, c2):
            return isBaseCategory(c2)
        case cat.T(True, _, _):
            return True
        case cat.N:
            return True
        case cat.Sbar(_):
            return True
        case cat.CONJ:
            return True
        case cat.LPAREN:
            return True
        case cat.RPAREN:
            return True
        case _:
            return False


def isArgumentCategory(c: Cat) -> bool:
    """A test to check if a given category is an argument category (i.e. not a base category)."""
    match c:
        case cat.NP(_):
            return not isNoncaseNP(c)
        case cat.Sbar(_):
            return True
        case _:
            return False


def isTNoncaseNP(c: Cat) -> bool:
    """A test to check if a given category is NPnc."""
    match c:
        case cat.BS(cat.T(_, _, _), x):
            return isNoncaseNP(x)
        case _:
            return False


def isNoncaseNP(c: Cat) -> bool:
    """A test to check if a given category is NPnc."""
    match c:
        case cat.NP([feature.F([v, *_])]):
            return FV.Nc in v
        case cat.NP([feature.SF(_, [_, v, *_])]):
            return FV.Nc in v
        case _:
            return False


def isBunsetsu(c: Cat) -> bool:
    """A test to check if a given category is the one that can appear on the left adjacent of a punctuation."""
    match c:
        case cat.SL(x, _):
            return isBunsetsu(x)
        case cat.BS(x, _):
            return isBunsetsu(x)
        case cat.LPAREN:
            return False
        case cat.S([_, f, *_]):
            match f:
                case feature.F(feat):
                    katsuyo = feat
                case feature.SF(_, feat):
                    katsuyo = feat
            if not {FV.Cont, FV.Term, FV.Attr, FV.Hyp, FV.Imper, FV.Pre, FV.NTerm, FV.NStem, FV.TeForm, FV.NiForm} | katsuyo:
                return False
            else:
                return True
        case cat.N:
            return False
        case _:
            return True


def endsWithT(c: Cat) -> bool:
    match c:
        case cat.SL(x, _):
            return endsWithT(x)
        case cat.T(_, _, _):
            return True
        case _:
            return False


def isNStem(c: Cat) -> bool:
    match c:
        case cat.BS(x, _):
            return isNStem(x)
        case cat.S([_, f, *_]):
            if unifyFeature([], f, feature.F([FV.NStem])):
                return True
            else:
                return False
        case _:
            return False


def unaryRules(_: Node, prevlist: list[Node]) -> list[Node]:
    """The function to apply all the unaryRules to a CCG node."""
    return prevlist


def binaryRules(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    return forwardFunctionCrossedSubstitutionRule(
        lnode, rnode,
        forwardFunctionCrossedComposition2Rule(
            lnode, rnode,
            forwardFunctionCrossedComposition1Rule(
                lnode, rnode,
                backwardFunctionComposition3Rule(
                    lnode, rnode,
                    backwardFunctionComposition2Rule(
                        lnode, rnode,
                        forwardFunctionComposition2Rule(
                            lnode, rnode,
                            backwardFunctionComposition1Rule(
                                lnode, rnode,
                                forwardFunctionComposition1Rule(
                                    lnode, rnode,
                                    backwardFunctionApplicationRule(
                                        lnode, rnode,
                                        forwardFunctionApplicationRule(
                                            lnode, rnode, prevlist
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def forwardFunctionApplicationRule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Forward function application rule."""
    if lnode.rs in [RuleSymbol.FFC1, RuleSymbol.FFC2, RuleSymbol.FFC3]:
        return prevlist
    match lnode.cat:
        case cat.SL(x, y1):
            match y1:
                case cat.T(True, _, _):
                    return prevlist
                case _:
                    inc = maximumIndexC(rnode.cat)
                    result = unifyCategory(
                        [], [], [], rnode.cat, incrementIndexC(y1, inc))
                    if result is None:
                        return prevlist
                    else:
                        _, csub, fsub = result
                        newcat = simulSubstituteCV(
                            csub, fsub, incrementIndexC(x, inc))
                        return [Node(
                            RuleSymbol.FFA,
                            lnode.pf + rnode.pf,
                            newcat,
                            [lnode, rnode],
                            lnode.score * rnode.score,
                            "",
                        )] + prevlist
        case _: return prevlist


def backwardFunctionApplicationRule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Backward function application rule."""
    if rnode.rs in [RuleSymbol.BFC1, RuleSymbol.BFC2, RuleSymbol.BFC3]:
        return prevlist
    match rnode.cat:
        case cat.BS(x, y2):
            inc = maximumIndexC(lnode.cat)
            result = unifyCategory(
                [], [], [], lnode.cat, incrementIndexC(y2, inc))
            if result is None:
                return prevlist
            else:
                _, csub, fsub = result
                newcat = simulSubstituteCV(
                    csub, fsub, incrementIndexC(x, inc))
                return [Node(
                    RuleSymbol.BFA,
                    lnode.pf + rnode.pf,
                    newcat,
                    [lnode, rnode],
                    lnode.score * rnode.score,
                    "",
                )] + prevlist
        case _: return prevlist


def forwardFunctionComposition1Rule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Forward function composition rule."""
    if lnode.rs in [RuleSymbol.FFC1, RuleSymbol.FFC2, RuleSymbol.FFC3]:
        return prevlist
    match (lnode.cat, rnode.cat):
        case (cat.SL(x, y1), cat.SL(y2, z)):
            if isTNoncaseNP(y1):
                return prevlist
            inc = maximumIndexC(rnode.cat)
            result = unifyCategory(
                [], [], [], y2, incrementIndexC(y1, inc))
            if result is None:
                return prevlist
            (_, csub, fsub) = result
            _z = simulSubstituteCV(csub, fsub, z)
            if numberOfArguments(_z) > 3:
                return prevlist
            newcat = cat.SL(simulSubstituteCV(
                csub, fsub, incrementIndexC(x, inc)), _z)
            return [Node(
                RuleSymbol.FFC1,
                lnode.pf + rnode.pf,
                newcat,
                [lnode, rnode],
                lnode.score * rnode.score,
                "",
            )] + prevlist
        case _: return prevlist


def backwardFunctionComposition1Rule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Backward function composition rule."""
    if rnode.rs in [RuleSymbol.BFC1, RuleSymbol.BFC2, RuleSymbol.BFC3]:
        return prevlist
    match (lnode.cat, rnode.cat):
        case (cat.BS(y1, z), cat.BS(x, y2)):
            inc = maximumIndexC(lnode.cat)
            result = unifyCategory(
                [], [], [], y1, incrementIndexC(y2, inc))
            if result is None:
                return prevlist

            (_, csub, fsub) = result
            newcat = simulSubstituteCV(
                csub, fsub, cat.BS(incrementIndexC(x, inc), z))
            return [Node(
                RuleSymbol.BFC1,
                lnode.pf + rnode.pf,
                newcat,
                [lnode, rnode],
                lnode.score * rnode.score,
                "",
            )] + prevlist
        case _: return prevlist


def forwardFunctionComposition2Rule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Forward function composition rule 2."""
    # TODO: Test required.
    if lnode.rs in [RuleSymbol.FFC1, RuleSymbol.FFC2, RuleSymbol.FFC3]:
        return prevlist
    match (lnode.cat, rnode.cat):
        case (cat.SL(x, y1), cat.SL(cat.SL(y2, z1), z2)):
            if isTNoncaseNP(y1):
                return prevlist
            inc = maximumIndexC(rnode.cat)
            result = unifyCategory(
                [], [], [], incrementIndexC(y1, inc), y2)
            if result is None:
                return prevlist
            (_, csub, fsub) = result
            _z1 = simulSubstituteCV(csub, fsub, z1)
            if numberOfArguments(_z1) > 2:
                return prevlist
            newcat = simulSubstituteCV(
                csub, fsub, cat.SL(cat.SL(incrementIndexC(x, inc), _z1), z2))
            return [Node(
                RuleSymbol.FFC2,
                lnode.pf + rnode.pf,
                newcat,
                [lnode, rnode],
                lnode.score * rnode.score,
                "",
            )] + prevlist
        case _: return prevlist


def backwardFunctionComposition2Rule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Backward function composition rule 2."""
    # TODO: Test required.
    if rnode.rs in [RuleSymbol.BFC1, RuleSymbol.BFC2, RuleSymbol.BFC3]:
        return prevlist
    match (lnode.cat, rnode.cat):
        case (cat.BS(cat.BS(y1, z1), z2), cat.BS(x, y2)):
            inc = maximumIndexC(lnode.cat)
            result = unifyCategory(
                [], [], [], incrementIndexC(y2, inc), y1)
            if result is None:
                return prevlist
            (_, csub, fsub) = result
            newcat = simulSubstituteCV(
                csub, fsub, cat.BS(cat.BS(incrementIndexC(x, inc), z1), z2))
            return [Node(
                RuleSymbol.BFC2,
                lnode.pf + rnode.pf,
                newcat,
                [lnode, rnode],
                lnode.score * rnode.score,
                "",
            )] + prevlist
        case _: return prevlist


def backwardFunctionComposition3Rule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Backward function composition rule 3."""
    # TODO: Test required.
    if rnode.rs in [RuleSymbol.BFC1, RuleSymbol.BFC2, RuleSymbol.BFC3]:
        return prevlist
    match (lnode.cat, rnode.cat):
        case (cat.BS(cat.BS(cat.BS(y1, z1), z2), z3), cat.BS(x, y2)):
            inc = maximumIndexC(lnode.cat)
            result = unifyCategory(
                [], [], [], incrementIndexC(y2, inc), y1)
            if result is None:
                return prevlist
            (_, csub, fsub) = result
            newcat = simulSubstituteCV(
                csub, fsub, cat.BS(cat.BS(cat.BS(incrementIndexC(x, inc), z1), z2), z3))
            return [Node(
                RuleSymbol.BFC3,
                lnode.pf + rnode.pf,
                newcat,
                [lnode, rnode],
                lnode.score * rnode.score,
                "",
            )] + prevlist
        case _: return prevlist


def forwardFunctionCrossedComposition1Rule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Forward function crossed composition rule."""
    # TODO: Test required.
    if rnode.rs in [RuleSymbol.FFC1, RuleSymbol.FFC2, RuleSymbol.FFC3]:
        return prevlist
    match (lnode.cat, rnode.cat):
        case (cat.SL(x, y1), cat.BS(y2, z)):
            if isTNoncaseNP(y1) or not isArgumentCategory(z):
                return prevlist
            inc = maximumIndexC(rnode.cat)
            result = unifyCategory(
                [], [], [], y2, incrementIndexC(y1, inc))
            if result is None:
                return prevlist
            (_, csub, fsub) = result
            z_ = simulSubstituteCV(csub, fsub, z)
            newcat = cat.BS(simulSubstituteCV(
                csub, fsub, incrementIndexC(x, inc)), z_)
            return [Node(
                RuleSymbol.FFCx1,
                lnode.pf + rnode.pf,
                newcat,
                [lnode, rnode],
                lnode.score * rnode.score * 0.01,
                "",
            )] + prevlist
        case _: return prevlist


def forwardFunctionCrossedComposition2Rule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Forward function crossed composition rule 2."""
    # TODO: Test required.
    if rnode.rs in [RuleSymbol.FFC1, RuleSymbol.FFC2, RuleSymbol.FFC3, RuleSymbol.EC]:
        return prevlist
    match (lnode.cat, rnode.cat):
        case (cat.SL(x, y1), cat.BS(cat.BS(y2, z1), z2)):
            if isTNoncaseNP(y1) or not isArgumentCategory(z2) or not isArgumentCategory(z1):
                return prevlist
            inc = maximumIndexC(rnode.cat)
            result = unifyCategory(
                [], [], [], incrementIndexC(y1, inc), y2)
            if result is None:
                return prevlist
            (_, csub, fsub) = result
            z1_ = simulSubstituteCV(csub, fsub, z1)
            if numberOfArguments(z1_) > 2:
                return prevlist
            newcat = simulSubstituteCV(
                csub, fsub, cat.BS(cat.BS(incrementIndexC(x, inc), z1_), z2))
            return [Node(
                RuleSymbol.FFCx2,
                lnode.pf + rnode.pf,
                newcat,
                [lnode, rnode],
                lnode.score * rnode.score * 0.01,
                "",
            )] + prevlist


def forwardFunctionCrossedSubstitutionRule(lnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Forward function crossed substitution rule."""
    # TODO: Test required.
    match (lnode.cat, rnode.cat):
        case (cat.BS(cat.SL(x, y1), z1), cat.BS(y2, z2)):
            if not isArgumentCategory(z1) or not isArgumentCategory(z2):
                return prevlist
            inc = maximumIndexC(rnode.cat)
            result = unifyCategory(
                [], [], [], incrementIndexC(z1, inc), z2)
            if result is None:
                return prevlist
            (z, csub1, fsub1) = result
            result = unifyCategory(
                csub1, fsub1, [], incrementIndexC(y1, inc), y2)
            if result is None:
                return prevlist
            (_, csub2, fsub2) = result
            newcat = simulSubstituteCV(
                csub2, fsub2, cat.BS(incrementIndexC(x, inc), z))
            return [Node(
                RuleSymbol.FFSx,
                lnode.pf + rnode.pf,
                newcat,
                [lnode, rnode],
                lnode.score * rnode.score * 0.01,
                "",
            )] + prevlist


def coordinationRule(lnode: Node, cnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Coordination rule."""
    # TODO: Test required.
    if lnode.rs == RuleSymbol.COORD:
        return prevlist
    if (endsWithT(rnode.cat) or isNStem(rnode.cat)) and lnode.cat == rnode.cat:
        return [Node(
            RuleSymbol.COORD,
            lnode.pf + cnode.pf + rnode.pf,
            rnode.cat,
            [lnode, cnode, rnode],
            lnode.score * rnode.score,
            "",
        )] + prevlist
    return prevlist


def parenthesisRule(lnode: Node, cnode: Node, rnode: Node, prevlist: list[Node]) -> list[Node]:
    """Parenthesis rule."""
    if lnode.cat == cat.LPAREN and rnode.cat == cat.RPAREN:
        return [Node(
            RuleSymbol.PAREN,
            lnode.pf + cnode.pf + rnode.pf,
            cnode.cat,
            [lnode, cnode, rnode],
            cnode.score,
            "",
        )] + prevlist
    return prevlist


def numberOfArguments(c: Cat) -> int:
    match c:
        case cat.SL(c1, _):
            return 1 + numberOfArguments(c1)
        case cat.BS(c1, _):
            return 1 + numberOfArguments(c1)
        case _: return 0


def maximumIndexC(c: Cat) -> int:
    match c:
        case cat.T(_, i, c2):
            return max(i, maximumIndexC(c2))
        case cat.SL(c1, c2):
            return max(maximumIndexC(c1), maximumIndexC(c2))
        case cat.BS(c1, c2):
            return max(maximumIndexC(c1), maximumIndexC(c2))
        case cat.S(f):
            return maximumIndexF(f)
        case cat.NP(f):
            return maximumIndexF(f)
        case cat.Sbar(f):
            return maximumIndexF(f)
        case _: return 0


"""
maximumIndexF :: [Feature] -> Int
maximumIndexF fs = case fs of
  [] -> 0
  ((SF i _):fs2) -> max i (maximumIndexF fs2)
  (_:fs2) -> maximumIndexF fs2
"""


def maximumIndexF(fs: list[Feature]) -> int:
    match fs:
        case []:
            return 0
        case [feature.SF(i, _), *fs2]:
            return max(i, maximumIndexF(fs2))
        case [_, *fs2]:
            return maximumIndexF(fs2)


def incrementIndexC(c: Cat, i: int) -> Cat:
    match c:
        case cat.T(f, j, u):
            return cat.T(f, i+j, incrementIndexC(u, i))
        case cat.SL(c1, c2):
            return cat.SL(incrementIndexC(c1, i), incrementIndexC(c2, i))
        case cat.BS(c1, c2):
            return cat.BS(incrementIndexC(c1, i), incrementIndexC(c2, i))
        case cat.S(f):
            return cat.S(incrementIndexF(f, i))
        case cat.Sbar(f):
            return cat.Sbar(incrementIndexF(f, i))
        case cat.NP(f):
            return cat.NP(incrementIndexF(f, i))
        case _: return c


def incrementIndexF(fs: list[Feature], i: int) -> list[Feature]:
    match fs:
        case []:
            return []
        case [feature.SF(j, f2), *fs2]:
            return [feature.SF(i+j, f2)] + incrementIndexF(fs2, i)
        case [fh, *ft]:
            return [fh] + incrementIndexF(ft, i)


def alter(i: int, v: int, mp: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return [(i, v)] + list(filter(lambda j: i != j, mp))


T1 = TypeVar("T1")


def fetchValue(sub: Assignment[T1], i: int, v: int) -> tuple[int, T1]:
    result = list(filter(lambda pair: i == pair[0], sub))
    if not result:
        return (i, v)

    match result[0]:
        case SubstLink(j):
            if j < i:
                return fetchValue(sub, j, v)
        # SubstVal[T1]の場合の処理
        case SubstVal(v2):
            return (i, v2)
        case _: return (i, v)


def simulSubstituteCV(csub: Assignment[Cat], fsub: Assignment[list[FV]], c: Cat) -> Cat:
    match c:
        case cat.T(_, i, _):
            return fetchValue(csub, i, c)[1]
        case cat.SL(ca, cb):
            return cat.SL(simulSubstituteCV(csub, fsub, ca), simulSubstituteCV(csub, fsub, cb))
        case cat.BS(ca, cb):
            return cat.BS(simulSubstituteCV(csub, fsub, ca), simulSubstituteCV(csub, fsub, cb))
        case cat.S(f):
            return cat.S(simulSubstituteFV(fsub, f))
        case cat.Sbar(f):
            return cat.Sbar(simulSubstituteFV(fsub, f))
        case cat.NP(f):
            return cat.NP(simulSubstituteFV(fsub, f))
        case _: return c


def unifyCategory(csub: Assignment[Cat], fsub: Assignment[list[FV]], banned: list[int], c1: Cat, c2: Cat) -> Optional[tuple[Cat, Assignment[Cat], Assignment[list[FV]]]]:
    """"""
    match c1:
        case cat.T(_, i, _):
            c1 = fetchValue(csub, i, c1)[1]
        case _: pass

    match c2:
        case cat.T(_, j, _):
            c2 = fetchValue(csub, j, c2)[1]
        case _: pass
    return unifyCategory2(csub, fsub, banned, c1, c2)


def unifyCategory2(csub: Assignment[Cat], fsub: Assignment[list[FV]], banned: list[int], c1: Cat, c2: Cat) -> Optional[tuple[Cat, Assignment[Cat], Assignment[list[FV]]]]:
    match (c1, c2):
        case (cat.T(f1, i, u1), cat.T(f2, j, u2)):
            if i in banned or j in banned:
                return None
            if i == j:
                return (c1, csub, fsub)
            ijmax = max(i, j)
            ijmin = min(i, j)
            if f1 and f2:
                (u3, csub2, fsub2) = unifyCategory2(
                    csub, fsub, [ijmin]+banned, u1, u2)
            elif f1:
                (u3, csub2, fsub2) = unifyWithHead(
                    csub, fsub, [ijmin]+banned, u1, u2)
            elif f2:
                (u3, csub2, fsub2) = unifyWithHead(
                    csub, fsub, [ijmin]+banned, u2, u1)
            else:
                (u3, csub2, fsub2) = unifyCategory2(
                    csub, fsub, [ijmin]+banned, u1, u2)
            result = cat.T(f1 and f2, ijmin, u3)
            return (result, alter(ijmin, SubstVal(result), alter(ijmax, SubstLink(ijmin), csub2)), fsub2)
        case (cat.T(f, i, u), _):
            if i in banned:
                return None
            else:
                if f:
                    (c3, csub2, fsub2) = unifyWithHead(
                        csub, fsub, [i]+banned, u, c2)
                else:
                    (c3, csub2, fsub2) = unifyCategory(
                        csub, fsub, [i]+banned, u, c2)
                return (c3, alter(i, SubstVal(c3), csub2), fsub2)
        case (_, cat.T(f, i, u)):
            if i in banned:
                return None
            else:
                if f:
                    (c3, csub2, fsub2) = unifyWithHead(
                        csub, fsub, [i] + banned, u, c1)
                else:
                    (c3, csub2, fsub2) = unifyCategory(
                        csub, fsub, [i] + banned, u, c1)
                return (c3, alter(i, SubstVal(c3), csub2), fsub2)
        case (cat.NP(f1), cat.NP(f2)):
            (f3, fsub2) = unifyFeatures(fsub, f1, f2)
            return (cat.NP(f3), csub, fsub2)
        case (cat.S(f1), cat.S(f2)):
            (f3, fsub2) = unifyFeatures(fsub, f1, f2)
            return (cat.S(f3), csub, fsub2)
        case (cat.Sbar(f1), cat.Sbar(f2)):
            (f3, fsub2) = unifyFeatures(fsub, f1, f2)
            return (cat.Sbar(f3), csub, fsub2)
        case (cat.SL(c3, c4), cat.SL(c5, c6)):
            (c7, csub2, fsub2) = unifyCategory(
                csub, fsub, banned, c4, c6)
            (c8, csub3, fsub3) = unifyCategory(
                csub2, fsub2, banned, c3, c5)
            return (cat.SL(c8, c7), csub3, fsub3)
        case (cat.BS(c3, c4), cat.BS(c5, c6)):
            (c7, csub2, fsub2) = unifyCategory(
                csub, fsub, banned, c4, c6)
            (c8, csub3, fsub3) = unifyCategory(
                csub2, fsub2, banned, c3, c5)
            return (cat.BS(c8, c7), csub3, fsub3)
        case (cat.N, cat.N):
            return (cat.N, csub, fsub)
        case (cat.CONJ, cat.CONJ):
            return (cat.CONJ, csub, fsub)
        case (cat.LPAREN, cat.LPAREN):
            return (cat.LPAREN, csub, fsub)
        case (cat.RPAREN, cat.RPAREN):
            return (cat.RPAREN, csub, fsub)
        case _:
            return None


def unifyWithHead(csub: Assignment[cat.Cat], fsub: Assignment[list[FV]], banned: list[int], c1: cat.Cat, c2: cat.Cat) -> Optional[tuple[cat.Cat, Assignment[cat.Cat], Assignment[list[FV]]]]:
    """
    unifies a cyntactic category `c1` (in `T True i c1`) with the head of `c2`, under a given feature assignment.
    """
    match c2:
        case cat.SL(x, y):
            x2, csub2, fsub2 = unifyWithHead(csub, fsub, banned, c1, x)
            return (cat.SL(x2, y), csub2, fsub2)
        case cat.BS(x, y):
            x2, csub2, fsub2 = unifyWithHead(csub, fsub, banned, c1, x)
            return (cat.BS(x2, y), csub2, fsub2)
        case cat.T(f, i, u):
            if i in banned:
                return None
            (x2, csub2, fsub2) = unifyCategory(csub, fsub, [i]+banned, c1, u)
            return (cat.T(f, i, x2), alter(i, SubstVal(cat.T(f, i, x2)), csub2), fsub2)
        case _: return unifyCategory(csub, fsub, banned, c1, c2)


def substituteFV(fsub: Assignment[list[FV]], f1: Feature) -> Feature:
    match f1:
        case feature.SF(i, v):
            j, v2 = fetchValue(fsub, i, v)
            return feature.SF(j, v2)
        case _: return f1


def simulSubstituteFV(fsub: Assignment[list[FV]], fs: list[Feature]) -> list[Feature]:
    return list(map(lambda f: substituteFV(fsub, f), fs))


def unifyFeature(fsub: Assignment[list[FV]], f1: Feature, f2: Feature) -> Optional[tuple[Feature, Assignment[list[FV]]]]:
    match (f1, f2):
        case (feature.SF(i, v1), feature.SF(j, v2)):
            if i == j:
                i2, v1_2 = fetchValue(fsub, i, v1)
                v3 = list(set(v1_2).intersection(v2))
                if len(v3) == 0:
                    return None
                else:
                    return (feature.SF(i2, v3), alter(i2, SubstVal(v3), fsub))
            else:
                i2, v1_2 = fetchValue(fsub, i, v1)
                j2, v2_2 = fetchValue(fsub, j, v2)
                v3 = list(set(v1_2).intersection(v2_2))
                if len(v3) == 0:
                    return None
                else:
                    ijmax = max(i2, j2)
                    ijmin = min(i2, j2)
                    return (feature.SF(ijmin, v3), alter(ijmax, SubstLink(ijmin), alter(ijmin, SubstVal(v3), fsub)))
        case (feature.SF(i, v1), feature.F(v2)):
            i2, v1_2 = fetchValue(fsub, i, v1)
            v3 = list(set(v1_2).intersection(v2))
            if len(v3) == 0:
                return None
            else:
                return (feature.SF(i2, v3), alter(i2, SubstVal(v3), fsub))
        case (feature.F(v1), feature.SF(j, v2)):
            j2, v2_2 = fetchValue(fsub, j, v2)
            v3 = list(set(v1).intersection(v2_2))
            if len(v3) == 0:
                return None
            else:
                return (feature.SF(j2, v3), alter(j2, SubstVal(v3), fsub))
        case (feature.F(v1), feature.F(v2)):
            v3 = list(set(v1).intersection(v2))
            if len(v3) == 0:
                return None
            else:
                return (feature.F(v3), fsub)


def unifyFeatures(fsub: Assignment[list[FV]], f1: list[Feature], f2: list[Feature]) -> Optional[tuple[list[Feature], Assignment[list[FV]]]]:
    match (f1, f2):
        case ([], []):
            return ([], fsub)
        case ((f1h, *f1t), (f2h, *f2t)):
            f3h, fsub2 = unifyFeature(fsub, f1h, f2h)
            f3t, fsub3 = unifyFeatures(fsub2, f1t, f2t)
            return ([f3h, f3t], fsub3)
        case _: return None


def testFFA():
    lnode = Node(
        rs=RuleSymbol.LEX,
        pf="美味しい",
        cat=cat.SL(cat.NP([feature.F([FV.Nc])]), cat.NP([feature.F([FV.Nc])])),
        daughters=[],
        score=-2,
        source=""
    )
    rnode = Node(
        rs=RuleSymbol.LEX,
        pf="パン",
        cat=cat.NP([feature.F([FV.Nc])]),
        daughters=[],
        score=-3,
        source=""
    )

    result = forwardFunctionApplicationRule(lnode, rnode, [])
    assert len(result) > 0
    assert result[0].rs == RuleSymbol.FFA
    assert result[0].pf == "美味しいパン"
    assert result[0].cat == cat.NP([feature.F([FV.Nc])])
    assert result[0].daughters == [lnode, rnode]
    assert result[0].score == 6
    assert result[0].source == ""


def testBFA():
    lnode = Node(
        rs=RuleSymbol.LEX,
        pf="僕が",
        cat=cat.NP([feature.F([FV.Ga])]),
        daughters=[],
        score=-3,
        source=""
    )
    rnode = Node(
        rs=RuleSymbol.LEX,
        pf="行く",
        cat=cat.BS(cat.S([feature.F([FV.V5k]), feature.F(
            [FV.Term])]), cat.NP([feature.F([FV.Ga])])),
        daughters=[],
        score=-4,
        source=""
    )

    result = backwardFunctionApplicationRule(lnode, rnode, [])
    assert len(result) > 0
    assert result[0].rs == RuleSymbol.BFA
    assert result[0].pf == "僕が行く"
    assert result[0].cat == cat.S([feature.F([FV.V5k]), feature.F([FV.Term])])
    assert result[0].daughters == [lnode, rnode]
    assert result[0].score == 12
    assert result[0].source == ""


def testFFC():
    lnode = Node(
        rs=RuleSymbol.LEX,
        pf="",
        cat=cat.SL(cat.NP([feature.F([FV.Nc])]), cat.NP([feature.F([FV.Nc])])),
        daughters=[],
        score=-2,
        source=""
    )
    rnode = Node(
        rs=RuleSymbol.LEX,
        pf="",
        cat=cat.SL(cat.NP([feature.F([FV.Nc])]), cat.NP([feature.F([FV.Nc])])),
        daughters=[],
        score=-3,
        source=""
    )

    result = forwardFunctionComposition1Rule(lnode, rnode, [])
    assert len(result) > 0
    assert result[0].rs == RuleSymbol.FFC1
    assert result[0].pf == ""
    assert result[0].cat == cat.SL(
        cat.NP([feature.F([FV.Nc])]), cat.NP([feature.F([FV.Nc])]))
    assert result[0].daughters == [lnode, rnode]
    assert result[0].score == 6


adjective: list[FV] = [FV.Aauo, FV.Ai, FV.ANAS, FV.ATII, FV.ABES]
node_です = Node(
    rs=RuleSymbol.LEX,
    pf="です",
    cat=cat.BS(
        cat.S([
            feature.SF(1, adjective),
            feature.F([FV.Term]),
            feature.SF(2, [FV.P, FV.M]),
            feature.F([FV.P]),
            feature.F([FV.M]),
            feature.F([FV.M]),
            feature.F([FV.M])]
        ),
        cat.S([
            feature.SF(1, adjective),
            feature.F([FV.Term]),
            feature.SF(2, [FV.P, FV.M]),
            feature.F([FV.M]),
            feature.F([FV.M]),
            feature.F([FV.M]),
            feature.F([FV.M])
        ])
    ),
    daughters=[],
    score=-0.1,
    source=""
)


def testBFC():
    lnode = Node(
        rs=RuleSymbol.LEX,
        pf="長い",
        cat=constructPredicate("長い", [FV.Ai], [FV.Term, FV.Attr]),
        daughters=[],
        score=-4,
        source=""
    )
    rnode = node_です

    result = backwardFunctionComposition1Rule(lnode, rnode, [])
    assert len(result) > 0
    assert result[0].rs == RuleSymbol.BFC1
    assert result[0].pf == "長いです"
    assert result[0].cat == cat.BS(
        cat.S([
            feature.SF(1, adjective),
            feature.F([FV.Term]),
            feature.SF(2, [FV.P, FV.M]),
            feature.F([FV.P]),
            feature.F([FV.M]),
            feature.F([FV.M]),
            feature.F([FV.M]),
        ]),
        cat.NP([feature.F([FV.Ga])])
    )
    assert result[0].daughters == [lnode, rnode]
    assert result[0].score == 0.4
    assert result[0].source == ""


if __name__ == "__main__":
    np = cat.NP([])
    sbar = cat.Sbar([])
    t = cat.T(False, 0, sbar)
    sl = cat.SL(np, t)
    testFFA()
    testBFA()
    testFFC()
    testBFC()
