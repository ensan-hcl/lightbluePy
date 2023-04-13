from feature import FeatureValue as FV
import feature
import cat
from node import Node
from lexicon.myLexicon import emptyCategories, myLexicon
from lexicon.template import defS, lexicalitem, modifiableS, anyPos, verbCat, verb
from lexicon.juman import jumanCompoundNouns
from cat import Cat

from functools import reduce


def setupLexicon(sentence: str) -> list[Node]:
    # 1. Setting up lexical items provided by JUMAN++
    with open("source/lexicon/Juman.dic.tsv") as f:
        jumandic = f.read()
        jumandic = [line for line in jumandic.split("\n") if line]
    jumandicFiltered = filter(lambda l: l[0] in sentence,
                              map(lambda l: l.split("\t"), jumandic))

    jumandicParsed = []
    cn: dict[str, tuple[str, int]] = dict()
    pn: dict[str, tuple[str, int]] = dict()
    for jumanline in jumandicFiltered:
        parseJumanLine(jumandicParsed, jumanline, cn, pn)

    # 2. Setting up private lexicon
    mylexiconFiltered = list(filter(lambda l: l.pf in sentence, myLexicon))
    # 3. Setting up compound nouns (returned from an execution of JUMAN)
    jumanCN = []  # jumanCompoundNouns(sentence.replace("―", "、"))
    # 4. Accumulating common nons and proper names entries
    commonnouns = list(map(lambda l: lexicalitem(
        l[0], "(CN)", int(l[1][1]), cat.N), cn.items()))
    # ((`SL`
    # (T True 1 modifiableS)
    # (`BS`
    #   (T True 1 modifiableS)
    #   NP [F[Nc]]
    # )
    # ))
    pn_cat = cat.SL(cat.T(True, 1, modifiableS),
                    cat.BS(cat.T(True, 1, modifiableS),
                           cat.NP([feature.F([FV.Nc])])
                           )
                    )

    propernames = list(map(lambda l: lexicalitem(
        l[0], "(PN)", int(l[1][1]), pn_cat), pn.items()))
    # 5. 1+2+3+4
    print([(lex.pf, lex.source, lex.rs) for lex in jumandicParsed])
    print([(lex.pf, lex.source) for lex in commonnouns])
    print([(lex.pf, lex.source) for lex in mylexiconFiltered])
    print([(lex.pf, lex.source) for lex in propernames])
    print([(lex.pf, lex.source) for lex in jumanCN])

    numeration = jumandicParsed + commonnouns + \
        mylexiconFiltered + propernames + jumanCN

    return numeration


def parseJumanLine(lexicalitems: list[Node], jumanline: list[str], commonnouns: dict[str, tuple[str, int]], propernames: dict[str, tuple[str, int]]) -> None:
    if len(jumanline) == 0:
        return
    # 相容れな	99	形容詞:イ形容詞アウオ段	相容れない	あいいれない	ContentW
    hyoki, score, cat, daihyo, yomi, source, caseframe = jumanline
    if cat.startswith("名詞:普通名詞"):
        commonnouns[hyoki] = (daihyo+"/"+yomi, int(score))
    elif cat.startswith("名詞:固有名詞") or cat.startswith("名詞:人名") or cat.startswith("名詞:地名") or cat.startswith("名詞:組織名"):
        propernames[hyoki] = (daihyo+"/"+yomi, int(score))
    else:
        catsemlist = jumanPos2Cat(daihyo+"/"+yomi, cat, caseframe)
        lexicalitems += list(map(lambda l: lexicalitem(hyoki,
                             "(J"+source[:3]+")", int(score), l), catsemlist))


def jumanPos2Cat(daihyo: str, ct: str, caseframe: str) -> list[Cat]:
    if ct.startswith("名詞:副詞的名詞"):
        return constructSubordinateConjunction(daihyo)
    elif ct.startswith("名詞:時相名詞"):
        return constructPredicate(daihyo, [FV.Nda, FV.Nna, FV.Nno, FV.Nni, FV.Nemp], [FV.NStem])
    elif ct.startswith("動詞:子音動詞カ行促音便形"):
        return constructVerb(daihyo, caseframe, [FV.V5IKU, FV.V5YUK], [FV.Stem])
    elif ct.startswith("動詞:子音動詞カ行"):
        return constructVerb(daihyo, caseframe, [FV.V5k], [FV.Stem])
    elif ct.startswith("動詞:子音動詞サ行"):
        return constructVerb(daihyo, caseframe, [FV.V5s], [FV.Stem])
    elif ct.startswith("動詞:子音動詞タ行"):
        return constructVerb(daihyo, caseframe, [FV.V5t], [FV.Stem])
    elif ct.startswith("動詞:子音動詞ナ行"):
        return constructVerb(daihyo, caseframe, [FV.V5n], [FV.Stem])
    elif ct.startswith("動詞:子音動詞マ行"):
        return constructVerb(daihyo, caseframe, [FV.V5m], [FV.Stem])
    elif ct.startswith("動詞:子音動詞ラ行イ形"):
        return constructVerb(daihyo, caseframe, [FV.V5NAS], [FV.Stem])
    elif ct.startswith("動詞:子音動詞ラ行"):
        return constructVerb(daihyo, caseframe, [FV.V5r], [FV.Stem])
    elif ct.startswith("動詞:子音動詞ワ行文語音便形"):
        return constructVerb(daihyo, caseframe, [FV.V5TOW], [FV.Stem])
    elif ct.startswith("動詞:子音動詞ワ行"):
        return constructVerb(daihyo, caseframe, [FV.V5w], [FV.Stem])
    elif ct.startswith("動詞:子音動詞ガ行"):
        return constructVerb(daihyo, caseframe, [FV.V5g], [FV.Stem])
    elif ct.startswith("動詞:子音動詞バ行"):
        return constructVerb(daihyo, caseframe, [FV.V5b], [FV.Stem])
    elif ct.startswith("動詞:母音動詞"):
        return constructVerb(daihyo, caseframe, [FV.V1], [FV.Stem, FV.Neg, FV.Cont, FV.NegL, FV.EuphT])
    elif ct.startswith("動詞:カ変動詞"):
        return constructVerb(daihyo, caseframe, [FV.VK], [FV.Stem])
    elif ct.startswith("名詞:サ変名詞"):
        return ((constructCommonNoun(daihyo)) + (constructVerb(daihyo, caseframe, [FV.VS, FV.VSN], [FV.Stem]))
                + (constructPredicate(daihyo, [FV.Nda, FV.Ntar], [FV.NStem])))
    elif ct.startswith("動詞:サ変動詞"):
        return constructVerb(daihyo, caseframe, [FV.VS], [FV.Stem])
    elif ct.startswith("動詞:ザ変動詞"):
        return constructVerb(daihyo, caseframe, [FV.VZ], [FV.Stem])
    elif ct.startswith("動詞:動詞性接尾辞ます型"):
        return constructVerb(daihyo, caseframe, [FV.V5NAS], [FV.Stem])
    elif ct.startswith("形容詞:イ形容詞アウオ段"):
        return constructVerb(daihyo, caseframe, [FV.Aauo], [FV.Stem])
    elif ct.startswith("形容詞:イ形容詞イ段"):
        return constructVerb(daihyo, caseframe, [FV.Ai], [FV.Stem, FV.Term])
    elif ct.startswith("形容詞:イ形容詞イ段特殊"):
        # 大きい
        return constructVerb(daihyo, caseframe, [FV.Ai, FV.Nna], [FV.Stem])
    elif ct.startswith("形容詞:ナ形容詞"):
        return constructVerb(daihyo, caseframe, [FV.Nda, FV.Nna, FV.Nni], [FV.NStem])
    elif ct.startswith("形容詞:ナ形容詞特殊"):
        # 同じ
        return constructVerb(daihyo, caseframe, [FV.Nda, FV.Nna], [FV.NStem])
    elif ct.startswith("形容詞:ナノ形容詞"):
        return constructVerb(daihyo, caseframe, [FV.Nda, FV.Nna, FV.Nno, FV.Nni], [FV.NStem])
    elif ct.startswith("形容詞:タル形容詞"):
        return constructVerb(daihyo, caseframe, [FV.Ntar, FV.Nto], [FV.Stem])
    elif ct.startswith("副詞"):
        return (constructVerb(daihyo, caseframe, [FV.Nda, FV.Nna, FV.Nno, FV.Nni, FV.Nto, FV.Nemp], [FV.NStem])+constructCommonNoun(daihyo))
    elif ct.startswith("連体詞"):
        return constructNominalPrefix(daihyo)
    elif ct.startswith("接続詞"):
        return constructConjunction(daihyo)
    elif ct.startswith("接頭辞:名詞接頭辞"):
        return constructNominalPrefix(daihyo)
    elif ct.startswith("接頭辞:動詞接頭辞"):
        return [cat.SL(defS(verb, [FV.Stem]), defS(verb, [FV.Stem]))]
    elif ct.startswith("接頭辞:イ形容詞接頭辞"):
        return [cat.SL(cat.BS(defS([FV.Aauo], [FV.Stem]), cat.NP([feature.F([FV.Ga])])),
                       cat.BS(defS([FV.Aauo], [FV.Stem]),
                              cat.NP([feature.F([FV.Ga])]))
                       )]
    elif ct.startswith("接頭辞:ナ形容詞接頭辞"):
        return [cat.SL(cat.BS(defS([FV.Nda], [FV.NStem]), cat.NP([feature.F([FV.Ga])])),
                       cat.BS(defS([FV.Nda], [FV.NStem]),
                              cat.NP([feature.F([FV.Ga])]))
                       )]
    elif ct.startswith("接尾辞:名詞性名詞助数辞"):
        return constructNominalSuffix(daihyo)
    elif ct.startswith("接尾辞:名詞性特殊接尾辞"):
        return constructNominalSuffix(daihyo)
    elif ct.startswith("接尾辞:名詞性述語接尾辞"):
        return constructNominalSuffix(daihyo)
    elif ct.startswith("特殊:括弧始"):
        return [(cat.LPAREN)]
    elif ct.startswith("特殊:括弧終"):
        return [(cat.RPAREN)]
    elif ct.startswith("数詞"):
        return constructCommonNoun(daihyo)
    elif ct.startswith("感動詞"):
        return [(defS([FV.Exp], [FV.Term]))]
    else:
        return [(defS([FV.Exp], [FV.Term]))]


def lookupLexicon(word: str, lexicon: list[Node]) -> list[Node]:
    return list(filter(lambda l: l.pf == word, lexicon))


def constructPredicate(daihyo: str, posF: list[FV], conjF: list[FV]) -> list[Cat]:
    return [cat.BS(defS(posF, conjF), cat.NP([feature.F([FV.Ga])]))]


def constructCommonNoun(daihyo: str) -> list[Cat]:
    return [cat.NP([feature.F([FV.Ga])])]


def constructVerb(daihyo: str, caseframe: str, posF: list[FV], conjF: list[FV]) -> list[Cat]:
    if caseframe == "":
        caseframe = "ガ"
    caseframelist = caseframe.split("#")
    return [verbCat(cf, posF, conjF) for cf in caseframelist]


def constructNominalPrefix(daihyo: str) -> list[Cat]:
    return [cat.SL(cat.N, cat.N)]


def constructNominalSuffix(daihyo: str) -> list[Cat]:
    return [cat.BS(cat.N, cat.N)]


def constructConjunction(daihyo: str) -> list[Cat]:
    return [cat.SL(
        cat.T(False, 1, cat.S([feature.F(anyPos), feature.F([FV.Term, FV.NTerm, FV.Pre, FV.Imper]), feature.SF(2, [
              FV.P, FV.M]), feature.SF(3, [FV.P, FV.M]), feature.SF(4, [FV.P, FV.M]), feature.F([FV.M]), feature.F([FV.M])])),
        cat.T(False, 1, cat.S([feature.F(anyPos), feature.F([FV.Term, FV.NTerm, FV.Pre, FV.Imper]), feature.SF(2, [
              FV.P, FV.M]), feature.SF(3, [FV.P, FV.M]), feature.SF(4, [FV.P, FV.M]), feature.F([FV.M]), feature.F([FV.M])]))
    )]


def constructSubordinateConjunction(daihyo: str) -> list[Cat]:
    return [cat.BS(
        cat.SL(modifiableS, modifiableS),
        cat.S([feature.F(anyPos), feature.F([FV.Attr]), feature.SF(7, [FV.P, FV.M]), feature.SF(
            8, [FV.P, FV.M]), feature.SF(9, [FV.P, FV.M]), feature.F([FV.M]), feature.F([FV.M])])
    )]
