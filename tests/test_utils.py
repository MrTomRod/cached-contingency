from unittest import TestCase
from scipy.stats import fisher_exact
from cached_contingency.utils import odds_ratio
from .init_tests import np, is_equivalent


class Test(TestCase):
    def test_odds_ratio(self):
        for i in range(1000):
            a, b, c, d = (np.random.randint(20) for _ in range(4))
            or_orig, pval_orig = fisher_exact([[a, b], [c, d]])
            or_calc = odds_ratio(a, b, c, d)
            self.assertTrue(is_equivalent(or_orig, or_calc), msg=f'{or_orig=} != {or_calc=}; {[[a, b], [c, d]]}')
