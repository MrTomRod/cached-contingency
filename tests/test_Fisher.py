from unittest import TestCase

from .init_tests import *

from cached_contingency.CachedFisher import *

FISHER_COMBINATIONS_WITH_ODDS_RATIO = ['abcd', 'acbd', 'dbca', 'dcba']
FISHER_COMBINATIONS = ['abcd', 'acbd', 'badc', 'bdac', 'cadb', 'cdab', 'dbca', 'dcba']


class TestCachedFisher(TestCase):
    def test_premise_single_odds_ratio(self):
        for i in range(1000):
            # calculate with normal order
            a, b, c, d = (np.random.randint(20) for _ in range(4))
            stat_orig, pval_orig = fisher_exact([[a, b], [c, d]])
            assert 0 <= pval_orig <= 1

            # calculate after swap
            aa, bb, cc, dd = fisher_swap_odds_ratio(a, b, c, d)
            stat_swap, pval_swap = fisher_exact([[aa, bb], [cc, dd]])
            assert 0 <= pval_swap <= 1

            # ensure same result
            self.assertTrue(is_equivalent(stat_swap, stat_orig), msg=f'{stat_swap=} != {stat_orig=}; {[[a, b], [c, d]]}')
            self.assertTrue(is_equivalent(pval_swap, pval_orig), msg=f'{pval_swap=} != {pval_orig=}; {[[a, b], [c, d]]}')

    def test_swap_premise_with_odds_ratio(self):
        test_swap(
            func=lambda table: fisher_exact(table),
            expected_combinations=FISHER_COMBINATIONS_WITH_ODDS_RATIO
        )

    def test_premise_single(self):
        for i in range(1000):
            # calculate with normal order
            a, b, c, d = (np.random.randint(20) for _ in range(4))
            stat_orig, pval_orig = fisher_exact([[a, b], [c, d]])
            assert 0 <= pval_orig <= 1

            # calculate after swap
            aa, bb, cc, dd = fisher_swap(a, b, c, d)
            stat_swap, pval_swap = fisher_exact([[aa, bb], [cc, dd]])
            assert 0 <= pval_swap <= 1

            # ensure same result
            self.assertTrue(is_equivalent(pval_swap, pval_orig), msg=f'{pval_swap=} != {pval_orig=}; {[[a, b], [c, d]]}')

    def test_swap_string(self):
        for i in range(1000):
            # calculate and without swap
            a, b, c, d = (np.random.randint(20) for _ in range(4))
            aa, bb, cc, dd = fisher_swap(a, b, c, d)

            pval_orig = pickleable_fisher(f'{a},{b},{c},{d}')
            pval_swap = pickleable_fisher(f'{aa},{bb},{cc},{dd}')

            # ensure same result
            self.assertTrue(is_equivalent(pval_swap, pval_orig), msg=f'{pval_swap=} != {pval_orig=}; {[[a, b], [c, d]]}')

    def test_swap_premise(self):
        test_swap(
            func=lambda table: (0, fisher_exact(table)[1]),  # pvalue and dummy value
            expected_combinations=FISHER_COMBINATIONS
        )

    def test_swap_letters(self):
        for combination in permutations('abcd'):
            combination = ''.join(combination)
            res = ''.join(fisher_swap(*combination))

            print(combination, '->', res, combination in FISHER_COMBINATIONS)
            if combination in FISHER_COMBINATIONS:
                assert res == 'abcd', f'{res=} {combination=}'
            else:
                assert res != 'abcd', f'{res=} {combination=}'

    def test_single_fisher(self):
        cc = CachedFisher()

        for i in range(100):
            a, b, c, d = (np.random.randint(20) for _ in range(4))

            pval_cache = cc.get_or_create(a, b, c, d)
            stat_calc, pval_calc = fisher_exact([[a, b], [c, d]])

            self.assertTrue(np.isclose(pval_cache, min(1., pval_calc)), msg=f'{pval_cache=} != {pval_calc=}; {[[a, b], [c, d]]}')

    def test_many(self):
        cc = CachedFisher()

        test_df = pd.DataFrame(
            [(np.random.randint(20) for _ in range(4)) for _ in range(100)],
            columns=['c1r1', 'c2r1', 'c1r2', 'c2r2']
        )

        # create new
        cc.get_or_create_many(test_df)

        # load from cache
        cc.get_or_create_many(test_df)
