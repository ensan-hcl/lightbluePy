from dataclasses import dataclass
# enum
from typing import TypeAlias, Union
from functools import reduce

import cat
import feature
from cat import Cat

from feature import FeatureValue as FV
from node import Node
import CCG

from lexicon.lexicon import setupLexicon, emptyCategories, lookupLexicon
from lexicon.template import modifiableS, lexicalitem

"""
type Chart = M.Map (Int,Int) [CCG.Node]
"""
Chart: TypeAlias = dict[tuple[int, int], list[Node]]


def parse(beam: int, sentence: str) -> Chart:
    """Main parsing function to parse a Japanees sentence and generates a CYK-chart."""
    if sentence == "":
        return {}
    else:
        lexicon = setupLexicon(sentence.replace("―", "。"))
        print([(lex.pf, lex.source) for lex in lexicon])
        chart, _, _, _ = reduce(lambda acc, c: chartAccumulator(
            beam, lexicon, acc, c), purifyText(sentence), ({}, [0], 0, ""))
        return chart


def purifyText(text: str) -> str:
    """removes occurrences of non-letters from an input text."""
    if text == "":
        return ""
    else:
        c, t = text[0], text[1:]
        if c.isspace():
            return purifyText(t)
        elif c in "！？!?…「」◎○●▲△▼▽■□◆◇★☆※†‡.":
            return purifyText(t)
        elif c in "，,-―?／＼":
            return "、" + purifyText(t)
        else:
            return c + purifyText(t)


PartialChart: TypeAlias = tuple[Chart, list[int], int, str]
"""
quadruples representing a state during parsing:
- the parsed result (Chart) of the left of the pivot,
- the stack of ending positions of the previous 'separators' (i.e. '、','，',etc),
- the pivot (=the current parsing position), and
- the revsersed list of chars that has been parsed
"""


def chartAccumulator(beam: int, lexicon: list[Node], partialChart: PartialChart, c: str) -> PartialChart:
    chart, seplist, i, stack = partialChart
    print(c, stack)
    if c == "、":
        newchart = {((i, i+1), [andCONJ(c), emptyCM(c)]): chart.items()}
        newstack = c + stack
        return (newchart, ([i+1] + seplist), (i+1), newstack)
    elif c == "。":
        newchart = {((i, i+1), [andCONJ(c), emptyCM(c)]): chart.items()}
        newstack = c + stack
        return (newchart, ([i+1] + seplist), (i+1), newstack)
    else:
        newstack = c + stack
        newchart, _, _, _ = reduce(lambda acc, c: boxAccumulator(
            beam, lexicon, acc, c), newstack, (chart.copy(), "", i, i+1))
        newseps = [i+1] + seplist if c in ["「",
                                           "『"] else seplist[1:] if c in ["」", "』"] else seplist
        return (newchart, newseps, (i+1), newstack)


def punctFilter(sep: int, i: int, charList: list[tuple[tuple[int, int], list[Node]]], e: tuple[tuple[int, int], list[Node]]) -> list[tuple[tuple[int, int], list[Node]]]:
    from_, to = e[0]
    nodes = e[1]
    if to == i:
        return (((from_, to+1), list(filter(lambda n: CCG.isBunsetsu(n.cat), nodes))), e) + charList
    else:
        return e + charList


def andCONJ(c: str) -> Node:
    return lexicalitem(c, "punct", 100, cat.CONJ)


def emptyCM(c: str) -> Node:
    return lexicalitem(c, "punct", 99, cat.BS(cat.SL(cat.T(True, 1, modifiableS), cat.BS(cat.T(True, 1, modifiableS), cat.NP([feature.F([FV.Ga, FV.O])]))), feature.NP([FV.F([FV.Nc])])))


PartialBox: TypeAlias = tuple[Chart, str, int, int]


def boxAccumulator(beam: int, lexicon: list[Node], partialBox: PartialBox, c: str) -> PartialBox:
    chart, word, i, j = partialBox
    newword = c + word
    list0 = lookupLexicon(newword, lexicon) if len(newword) < 23 else []
    list1 = checkEmptyCategories(checkParenthesisRule(i, j, chart, checkCoordinationRule(
        i, j, chart, checkBinaryRules(i, j, chart, checkUnaryRules(list0)))))
    newchart = {k: v for k, v in chart.items()}
    # ここのソートを実装する
    newchart[(i, j)] = sorted(
        list1, key=lambda n: n.score, reverse=True)[:beam]
    return (newchart, newword, i-1, j)


def lookupChart(i: int, j: int, chart: Chart) -> list[Node]:
    return chart.get((i, j), [])


def checkUnaryRules(prevlist: list[Node]) -> list[Node]:
    return reduce(lambda acc, node: CCG.unaryRules(node, acc), prevlist, prevlist.copy())


def checkBinaryRules(i: int, j: int, chart: Chart, prevlist: list[Node]) -> list[Node]:
    return reduce(lambda acck, k:
                  reduce(lambda accl, lnode:
                         reduce(lambda accr, rnode:
                                CCG.binaryRules(lnode, rnode, accr),
                                lookupChart(k, j, chart),
                                accl.copy()
                                ),
                         lookupChart(i, k, chart),
                         acck.copy()
                         ),
                  range(i+1, j),
                  prevlist.copy()
                  )


def checkCoordinationRule(i: int, j: int, chart: Chart, prevlist: list[Node]) -> list[Node]:
    return reduce(lambda acck, k:
                  reduce(lambda accc, cnode:
                         reduce(lambda accl, lnode:
                                reduce(lambda accr, rnode:
                                       CCG.coordinationRule(
                                           lnode, cnode, rnode, accr),
                                       lookupChart(k+1, j, chart),
                                       accl.copy()
                                       ),
                                lookupChart(i, k, chart),
                                accc.copy()
                                ),
                         filter(lambda n: n.cat == cat.CONJ,
                                lookupChart(k, k+1, chart)),
                         acck.copy()
                         ),
                  range(i+1, j-1),
                  prevlist.copy()
                  )


def checkParenthesisRule(i: int, j: int, chart: Chart, prevlist: list[Node]) -> list[Node]:
    if i+3 <= j:
        return reduce(lambda accl, lnode:
                      reduce(lambda accr, rnode:
                             reduce(lambda accc, cnode:
                                    CCG.parenthesisRule(
                                        lnode, cnode, rnode, accc),
                                    lookupChart(i+1, j-1, chart),
                                    accr.copy()
                                    ),
                             filter(lambda n: n.cat == cat.RPAREN,
                                    lookupChart(j-1, j, chart)),
                             accl.copy()
                             ),
                      filter(lambda n: n.cat == cat.LPAREN,
                             lookupChart(i, i+1, chart)),
                      prevlist.copy()
                      )
    else:
        return prevlist.copy()


"""
  foldl' (\p ec -> foldl' (\list node -> (CCG.binaryRules node ec) $ (CCG.binaryRules ec node) list) p p) prevlist L.emptyCategories
"""


def checkEmptyCategories(prevlist: list[Node]) -> list[Node]:
    assert prevlist is not None

    def update_inner(l: list[Node], node: Node, ec: Node):
        assert l is not None
        bin_ec_node = CCG.binaryRules(ec, node, l.copy())
        assert bin_ec_node is not None
        bin_node_ec = CCG.binaryRules(node, ec, bin_ec_node)
        assert bin_node_ec is not None
        return bin_node_ec

    def update_outer(p: list[Node], ec: Node):
        assert p is not None
        result = reduce(lambda l, node: update_inner(l, node, ec),
                        p, p.copy())
        assert result is not None
        return result

    return reduce(update_outer,
                  emptyCategories,
                  prevlist.copy()
                  )


def simpleParse(beam: int, sentence: str) -> list[Node]:
    chart = parse(beam, sentence)
    for key, value in chart.items():
        print(key, [node.pf for node in value])
    match extractParseResult(beam, chart):
        case Full(nodes):
            return nodes
        case Partial(nodes):
            return nodes
        case Failed():
            return []


@ dataclass
class Full:
    nodes: list[Node]


@ dataclass
class Partial:
    nodes: list[Node]


@ dataclass
class Failed:
    pass


ParseResult: TypeAlias = Union[Full, Partial, Failed]


def extractParseResult(beam: int, chart: Chart) -> ParseResult:
    def f(c: list[tuple[tuple[int, int], list[Node]]]) -> ParseResult:
        match c:
            case []:
                return Failed()
            case(((i, _), nodes), *_):
                if i == 0:
                    return Full(list(map(CCG.wrapNode, sortByNumberOfArgs(nodes))))
                else:
                    return Partial(g(list(map(CCG.wrapNode, sortByNumberOfArgs(nodes))), list(filter(lambda x: x[0][1] <= i, c))))
            case _:
                return Failed()

    def g(results: list[Node], cs: list[tuple[tuple[int, int], list[Node]]]) -> list[Node]:
        match cs:
            case []:
                return results
            case(((i, _), nodes), *_):
                return g([CCG.conjoinNodes(x, y) for x in map(CCG.wrapNode, nodes) for y in results][:beam], list(filter(lambda x: x[0][1] <= i, cs)))
    # isLessPrivilegedThanのお気持ち：n文字のやつに対して(0, n)を最優先したい。なぜならこれが一番長い範囲をパースできているから。
    # したがって、まず右側が一番大きいものを、次に左側が一番小さいものを選ぶ
    return f(list(sorted(filter(lambda x: len(x[1]) > 0, chart.items()), key=lambda x: (x[0][1], -x[0][0]), reverse=True)))


"""
-- PythonでisLessPrivilegedThanを再現するには、(x[1], -x[0])というタプルを使えば良い
-- | a `isLessPriviledgedThan` b means that b is more important parse result than a.
isLessPrivilegedThan :: ((Int,Int),a) -> ((Int,Int),a) -> Ordering
isLessPrivilegedThan ((i1,j1),_) ((i2,j2),_) | i1 == i2 && j1 == j2 = EQ
                                             | j2 > j1 = GT
                                             | j1 == j2 && i2 < i1 = GT
                                             | otherwise = LT

"""


def sortByNumberOfArgs(nodes: list[Node]) -> list[Node]:
    return sorted(nodes, key=lambda node: (numberOfArgs(node.cat), -node.score))


def numberOfArgs(c: Cat) -> int:
    match c:
        case cat.SL(x, _):
            return numberOfArgs(x) + 1
        case cat.BS(x, _):
            return numberOfArgs(x) + 1
        case cat.T(_, _, c):
            return numberOfArgs(c)
        case cat.S(_):
            return 1
        case cat.NP(_):
            return 10
        case cat.Sbar(_):
            return 0
        case cat.N:
            return 2
        case cat.CONJ:
            return 100
        case cat.LPAREN:
            return 100
        case cat.RPAREN:
            return 100
        case _:
            raise Exception(f"unknown category {c}")


def output_node(node: Node) -> str:
    indent = "    "
    newline = "\n"

    def add_indent(s: str) -> str:
        return newline.join([indent + line for line in s.split(newline)])
    return f"""Node(
{add_indent('rs       ='+str(node.rs))},
{add_indent('pf       ='+node.pf)},
{add_indent('cat      ='+output_cat(node.cat))},
{add_indent('source   ='+node.source)},
{add_indent('score    ='+str(node.score))},
{add_indent('daughters=[' + newline.join([output_node(n) for n in node.daughters]) + ']')},
)
"""


def output_cat(c1: Cat) -> str:
    indent = "    "
    newline = "\n"

    def add_indent(s: str) -> str:
        return newline.join([indent + line for line in s.split(newline)])
    match c1:
        case cat.SL(x, y):
            return f"""SL(
{add_indent(output_cat(x))}, 
{add_indent(output_cat(y))}
)"""
        case cat.BS(x, y):
            return f"""BS(
{add_indent(output_cat(x))}, 
{add_indent(output_cat(y))}
)"""
        case cat.T(b, i, c):
            return f"""T(
{indent}{b}, {i}, {output_cat(c)}
)"""
        case cat.S(f):
            return f"S{f}"
        case cat.NP(f):
            return f"NP{f}"
        case cat.Sbar(f):
            return f"Sbar{f}"
        case cat.N:
            return "N"
        case cat.CONJ:
            return "CONJ"
        case cat.LPAREN:
            return "LPAREN"
        case cat.RPAREN:
            return "RPAREN"
        case _:
            raise Exception(f"unknown category {c1}")


if __name__ == "__main__":

    res = simpleParse(10, "走る")
    for r in res[:3]:
        print(output_node(r))
