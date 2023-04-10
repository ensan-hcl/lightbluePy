
import cat
import feature
from feature import FeatureValue as FV


def defS(p: list[FV], c: list[FV]) -> cat.Cat:
    return cat.S([feature.F(p), feature.F(c), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M]), feature.F([FV.M])])
