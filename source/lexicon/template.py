
import cat
import feature
from feature import FeatureValue as FV
from feature import Feature
from node import Node, RuleSymbol


def lexicalitem(pf: str, source: str, score: int, cat: cat.Cat) -> Node:
    return Node(RuleSymbol.LEX, pf, cat, [], score / 100, source)


def defS(p: list[FV], c: list[FV]) -> cat.Cat:
    # check all features are valid (not a list)
    assert all(not isinstance(fv, list) for fv in p)
    assert all(not isinstance(fv, list) for fv in c)
    return cat.S([feature.F(p), feature.F(c), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M])])


verb: list[FV] = [FV.V5k, FV.V5s, FV.V5t, FV.V5n, FV.V5m, FV.V5r, FV.V5w, FV.V5g, FV.V5z, FV.V5b,
                  FV.V5IKU, FV.V5YUK, FV.V5ARU, FV.V5NAS, FV.V5TOW, FV.V1, FV.VK, FV.VS, FV.VSN, FV.VZ, FV.VURU]
adjective: list[FV] = [FV.Aauo, FV.Ai, FV.ANAS, FV.ATII, FV.ABES]
nomPred: list[FV] = [FV.Nda, FV.Nna, FV.Nno, FV.Nni, FV.Nemp, FV.Ntar]
anyPos: list[FV] = verb + adjective + nomPred
nonStem: list[FV] = [FV.Neg, FV.Cont, FV.Term, FV.Attr, FV.Hyp,
                     FV.Imper, FV.Pre, FV.NStem, FV.VoR, FV.VoS, FV.VoE, FV.NegL, FV.TeForm]

modifiableS = cat.S([feature.SF(2, anyPos), feature.SF(3, nonStem), feature.SF(
    4, [FV.P, FV.M]), feature.SF(5, [FV.P, FV.M]), feature.SF(6, [FV.P, FV.M]), feature.F([FV.M]), feature.F([FV.M])])


def verbCat(caseframe: str, posF: list[FV], conjF: list[FV]) -> cat.Cat:
    return verbCat_(caseframe, defS(posF, conjF))


def verbCat_(caseframe: str, ct: cat.Cat) -> cat.Cat:
    if caseframe == '':
        return ct
    c = caseframe[0]
    cs = caseframe[1:]
    if c == 'ガ':
        return verbCat_(cs, cat.BS(ct, cat.NP([feature.F([FV.Ga])])))
    if c == 'ヲ':
        return verbCat_(cs, cat.BS(ct, cat.NP([feature.F([FV.O])])))
    if c == 'ニ':
        return verbCat_(cs, cat.BS(ct, cat.NP([feature.F([FV.Ni])])))
    if c == 'ト':
        return verbCat_(cs, cat.BS(ct, cat.Sbar([feature.F([FV.ToCL])])))
    if c == 'ヨ':
        return verbCat_(cs, cat.BS(ct, cat.NP([feature.F([FV.Niyotte])])))
    if c == 'ノ':
        # 無視する
        return verbCat_(cs, ct)
    raise Exception('invalid case frame' + c)


m5: list[Feature] = [feature.F([FV.M]), feature.F(
    [FV.M]), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M])]
pmmmm: list[Feature] = [feature.F([FV.P]), feature.F(
    [FV.M]), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M])]
mpmmm: list[Feature] = [feature.F([FV.M]), feature.F(
    [FV.P]), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M])]
mmpmm: list[Feature] = [feature.F([FV.M]), feature.F(
    [FV.M]), feature.F([FV.P]), feature.F([FV.M]), feature.F([FV.M])]
mmmpm: list[Feature] = [feature.F([FV.M]), feature.F(
    [FV.M]), feature.F([FV.M]), feature.F([FV.P]), feature.F([FV.M])]
mppmm: list[Feature] = [feature.F([FV.M]), feature.F(
    [FV.P]), feature.F([FV.P]), feature.F([FV.M]), feature.F([FV.M])]
