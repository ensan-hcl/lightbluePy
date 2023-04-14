from node import Node, RuleSymbol
from cat import Cat
import feature
from feature import Feature
from feature import FeatureValue as FV
import cat
from lexicon.template import modifiableS, defS, verb, anyPos, adjective, nomPred,  nonStem, lexicalitem, m5, mmmpm, verbCat, mmpmm, mpmmm, mppmm
from lexicon.mylexicon_hs import empty_categories, my_lexicon

import lark
emptyCategories: list[Node] = []
myLexicon: list[Node] = []


def parse_fvs(tree: lark.Token) -> list[FV]:
    assert tree.data == "featurevalues"

    fvs = []
    for child in tree.children:
        if "data" in dir(child):
            match child.data:
                case "anypos_fvs":
                    fvs += anyPos
                case "verb_fvs":
                    fvs += verb
                case "adjective_fvs":
                    fvs += adjective
                case "nompred_fvs":
                    fvs += nomPred
                case "nonstem_fvs":
                    fvs += nonStem
                case "featurevalues":
                    fvs += parse_fvs(child)
                case _:
                    raise Exception("Unknown feature value: " + child.data)

        if "value" in dir(child) and child.value.startswith("[") and child.value.endswith("]"):
            child.value = child.value[1:-1]
            # ,で区切ってFVに変換する
            fvs.extend([FV[fv.strip()] for fv in child.value.split(",")])
    assert all(not isinstance(fv, list) for fv in fvs)
    return fvs


def parse_features(tree: lark.Token) -> list[Feature]:
    assert tree.data == "features"
    features = []
    for child in tree.children:
        match child.data:
            case "features":
                features += parse_features(child)
            case "mmmpm_features":
                features += mmmpm
            case "m5_features":
                features += m5
            case "mmpmm_features":
                features += mmpmm
            case "mpmmm_features":
                features += mpmmm
            case "mppmm_features":
                features += mppmm
            case "feature":
                assert len(child.children) == 1
                f = child.children[0]
                match f.data:
                    case "f_feature":
                        assert len(f.children) == 1
                        features.append(feature.F(parse_fvs(f.children[0])))
                    case "sf_feature":
                        assert len(f.children) == 2
                        features.append(feature.SF(
                            int(f.children[0].value), parse_fvs(f.children[1])))
                    case _:
                        raise Exception("Unknown feature: " + f.data)
            case _:
                raise Exception("Unknown feature: " + child.data)
    return features


def parse_bs_cat(tree: lark.Token) -> Cat:
    assert tree.data == "bs_cat"
    assert len(tree.children) == 2
    left = parse_cat(tree.children[0])
    right = parse_cat(tree.children[1])
    return cat.BS(left, right)


def parse_sl_cat(tree: lark.Token) -> Cat:
    assert tree.data == "sl_cat"
    assert len(tree.children) == 2
    left = parse_cat(tree.children[0])
    right = parse_cat(tree.children[1])
    return cat.SL(left, right)


def parse_t_cat(tree: lark.Token) -> Cat:
    assert tree.data == "t_cat"
    assert len(tree.children) == 3
    match tree.children[0]:
        case "True":
            is_closed = True
        case "False":
            is_closed = False
        case _:
            raise Exception("Unknown boolean: " + tree.children[0])
    index = int(tree.children[1])
    restriction = parse_cat(tree.children[2])
    return cat.T(is_closed, index, restriction)


def parse_np_cat(tree: lark.Token) -> Cat:
    assert tree.data == "np_cat"
    assert len(tree.children) == 1
    child = tree.children[0]
    return cat.NP(parse_features(child))


def parse_s_cat(tree: lark.Token) -> Cat:
    assert tree.data == "s_cat"
    assert len(tree.children) == 1
    child = tree.children[0]
    return cat.S(parse_features(child))


def parse_sbar_cat(tree: lark.Token) -> Cat:
    assert tree.data == "sbar_cat"
    assert len(tree.children) == 1
    child = tree.children[0]
    return cat.Sbar(parse_features(child))


def parse_defs_cat(tree: lark.Token) -> Cat:
    assert tree.data == "defs_cat"
    assert len(tree.children) == 2
    arg1 = parse_fvs(tree.children[0])
    arg2 = parse_fvs(tree.children[1])
    return defS(arg1, arg2)


def parse_cat(tree: lark.Token) -> Cat:
    assert tree.data == "cat"
    assert len(tree.children) == 1
    child = tree.children[0]
    match child.data:
        case "bs_cat":
            return parse_bs_cat(child)
        case "sl_cat":
            return parse_sl_cat(child)
        case "t_cat":
            return parse_t_cat(child)
        case "modifiables_cat":
            return modifiableS
        case "n_cat":
            return cat.N
        case "conj_cat":
            return cat.CONJ
        case "lparen_cat":
            return cat.LPAREN
        case "rparen_cat":
            return cat.RPAREN
        case "np_cat":
            return parse_np_cat(child)
        case "s_cat":
            return parse_s_cat(child)
        case "sbar_cat":
            return parse_sbar_cat(child)
        case "defs_cat":
            return parse_defs_cat(child)
        case "cat":
            return parse_cat(child)
        case _:
            raise Exception("Unknown cat type: " + child.data)


def parse_string(value: str) -> str:
    return value[1:-1]


def ec(word: str, source: str, r: int, c: Cat) -> Node:
    return Node(RuleSymbol.EC, word, c, [], r / 100, source)


def parse_ec_declaration(tree: lark.Token) -> Node:
    assert tree.data == "ec_declaration"
    assert len(tree.children) == 5
    word = parse_string(tree.children[0].children[0].value)
    source = parse_string(tree.children[1].children[0].value)
    value = tree.children[2].children[0].value
    cat = parse_cat(tree.children[3].children[0])
    # sem = parse_sem(tree.children[4].children[0])
    return ec(word, source, int(value), cat)


def mylex(words: list[str], source: str, cat: Cat) -> list[Node]:
    return [lexicalitem(word, source, 100, cat) for word in words]


def parse_mylex_declaration(tree: lark.Token) -> list[Node]:
    assert tree.data == "mylex_declaration"
    assert len(tree.children) == 4
    strings = [parse_string(child.value)
               for child in tree.children[0].children]
    source = parse_string(tree.children[1].children[0].value)
    cat = parse_cat(tree.children[2])
    # sem =
    return mylex(strings, source, cat)


def mylex2(words: list[str], source: str, value: int, cat: Cat) -> list[Node]:
    return [lexicalitem(word, source, value, cat) for word in words]


def parse_mylex2_declaration(tree: lark.Token) -> list[Node]:
    assert tree.data == "mylex2_declaration"
    assert len(tree.children) == 5
    strings = [parse_string(child.value)
               for child in tree.children[0].children]
    source = tree.children[1].children[0].value
    value = tree.children[2].children[0].value
    cat = parse_cat(tree.children[3])
    # sem =
    return mylex2(strings, source, int(value), cat)


"""
conjSuffix :: T.Text -> T.Text -> [FeatureValue] -> [FeatureValue] -> [Node]
conjSuffix wd num catpos catconj = [lexicalitem wd num 100 ((S ([SF 1 catpos, F catconj]++m5)) `BS` (S ([SF 1 catpos, F[Stem]]++m5))) (id,[])]
"""


def conjSuffix(word: str, source: str, catpos: list[FV], catconj: list[FV]) -> list[Node]:
    return [lexicalitem(word, source, 100, cat.BS(
        cat.S([feature.SF(1, catpos), feature.F(catconj)] + m5),
        cat.S([feature.SF(1, catpos), feature.F([FV.Stem])] + m5)
    ))]


def parse_conjsuffix_declaration(tree: lark.Token) -> list[Node]:
    assert tree.data == "conjsuffix_declaration"
    assert len(tree.children) == 4
    name = parse_string(tree.children[0].children[0].value)
    source = parse_string(tree.children[1].children[0].value)
    fvs1 = parse_fvs(tree.children[2])
    fvs2 = parse_fvs(tree.children[3])
    return conjSuffix(name, source, fvs1, fvs2)


def conjNSuffix(word: str, source: str, catpos: list[FV], catconj: list[FV]) -> list[Node]:
    return [lexicalitem(word, source, 100, cat.BS(
        cat.S([feature.SF(1, catpos), feature.F(catconj)] + m5),
        cat.S([feature.SF(1, catpos), feature.F([FV.NStem])] + m5)
    ))]


def parse_conjnsuffix_declaration(tree: lark.Token) -> list[Node]:
    assert tree.data == "conjnsuffix_declaration"
    assert len(tree.children) == 4
    name = parse_string(tree.children[0].children[0].value)
    source = parse_string(tree.children[1].children[0].value)
    fvs1 = parse_fvs(tree.children[2])
    fvs2 = parse_fvs(tree.children[3])
    return conjNSuffix(name, source, fvs1, fvs2)


def verblex(words: list[str], source: str, posF: list[FV], conjF: list[FV], daihyo: str, cf: str) -> list[Node]:
    return [lexicalitem(word, source, 100, verbCat(cf, posF, conjF)) for word in words]


def parse_verblex_declaration(tree: lark.Token) -> list[Node]:
    assert tree.data == "verblex_declaration"
    assert len(tree.children) == 7
    strings = [parse_string(child.value)
               for child in tree.children[0].children]
    source = parse_string(tree.children[1].children[0].value)
    fvs1 = parse_fvs(tree.children[2])
    fvs2 = parse_fvs(tree.children[3])
    daihyo = parse_string(tree.children[4].value)
    caseframes = parse_string(tree.children[5].value)
    # evt = parse_string(tree.children[6].children[0].value)
    result = []
    for cf in caseframes.split("#"):
        result += verblex(strings, source, fvs1, fvs2, daihyo, cf)
    return result


def load():
    # load the parser
    parser = lark.Lark.open("lexicon_haskell.lark",
                            rel_to=__file__, start="start")
    # parse
    global emptyCategories
    tree = parser.parse(empty_categories)
    for statement in tree.children:
        assert statement.data == "statement"
        match statement.children[0].data:
            case "ec_declaration":
                emptyCategories.append(
                    parse_ec_declaration(statement.children[0]))

            case _:
                raise Exception(f"unknown declaration {id}")

    global myLexicon
    tree = parser.parse(my_lexicon)
    for statement in tree.children:
        assert statement.data == "statement"
        match statement.children[0].data:
            case "ec_declaration":
                myLexicon.append(
                    parse_ec_declaration(statement.children[0]))
            case "mylex_declaration":
                myLexicon += parse_mylex_declaration(
                    statement.children[0])
            case "mylex2_declaration":
                myLexicon += parse_mylex2_declaration(
                    statement.children[0])
            case "conjsuffix_declaration":
                myLexicon += parse_conjsuffix_declaration(
                    statement.children[0]
                )
            case "conjnsuffix_declaration":
                myLexicon += parse_conjnsuffix_declaration(
                    statement.children[0]
                )
            case "verblex_declaration":
                myLexicon += parse_verblex_declaration(
                    statement.children[0]
                )
            case _:
                print(statement)
                raise Exception(
                    f"unknown declaration {statement.children[0].data}")


load()
