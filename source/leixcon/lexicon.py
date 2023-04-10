from feature import FeatureValue as FV
import feature
import cat
from leixcon.template import defS
"""
func constructPredicate(_ daihyo: String, _ posF: [FeatureValue], _ conjF: [FeatureValue]) -> Cat {
    return .BS(defS(posF, conjF), .NP([.F([.Ga])]))
}
"""


def constructPredicate(daihyo: str, posF: list[FV], conjF: list[FV]) -> cat.Cat:
    return cat.BS(defS(posF, conjF), cat.NP([feature.F([FV.Ga])]))
