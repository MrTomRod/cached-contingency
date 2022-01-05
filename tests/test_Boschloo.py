from unittest import TestCase

from .init_tests import *

from cached_contingency.CachedBoschloo import *

BOSCHLOO_COMBINATIONS = ['abcd', 'badc', 'cdab', 'dcba']


def boschloo_exact_like_fisher(table: [[int, int], [int, int]]) -> (float, float):
    res = boschloo_exact(table)
    return res.statistic, min(1., res.pvalue)  # same order as Fisher's, enforce pvalue below 1


class TestCachedBoschloo(TestCase):
    def test_premise_single(self):
        for i in range(50):
            # calculate with normal order
            a, b, c, d = (np.random.randint(20) for _ in range(4))
            stat_orig, pval_orig = boschloo_exact_like_fisher([[a, b], [c, d]])
            assert 0 <= pval_orig <= 1

            # calculate after swap
            aa, bb, cc, dd = boschloo_swap(a, b, c, d)
            stat_swap, pval_swap = boschloo_exact_like_fisher([[aa, bb], [cc, dd]])
            assert 0 <= pval_swap <= 1

            # ensure same result
            self.assertTrue(is_equivalent(pval_swap, pval_orig), msg=f'{pval_swap=} != {pval_orig=}; {[[a, b], [c, d]]}')
            self.assertTrue(is_equivalent(stat_swap, stat_orig), msg=f'{stat_swap=} != {stat_orig=}; {[[a, b], [c, d]]}')

    def test_swap_string(self):
        for i in range(100):
            # calculate and without swap
            a, b, c, d = (np.random.randint(20) for _ in range(4))
            aa, bb, cc, dd = boschloo_swap(a, b, c, d)

            pval_orig = pickleable_boschloo(f'{a},{b},{c},{d}')
            pval_swap = pickleable_boschloo(f'{aa},{bb},{cc},{dd}')

            # ensure same result
            self.assertTrue(is_equivalent(pval_swap, pval_orig), msg=f'{pval_swap=} != {pval_orig=}; {[[a, b], [c, d]]}')

    def test_swap_premise(self):
        test_swap(
            func=lambda table: (0, boschloo_exact(table).pvalue),  # pvalue and dummy value
            expected_combinations=BOSCHLOO_COMBINATIONS
        )

    def test_swap_alt_premise(self):
        test_swap(
            func=boschloo_exact_like_fisher,  # pvalue and dummy value
            expected_combinations=BOSCHLOO_COMBINATIONS
        )

    def test_swap_letters(self):
        for combination in permutations('abcd'):
            combination = ''.join(combination)
            res = ''.join(boschloo_swap(*combination))

            print(combination, '->', res, combination in BOSCHLOO_COMBINATIONS)
            if combination in BOSCHLOO_COMBINATIONS:
                assert res == 'abcd', f'{res=} {combination=}'
            else:
                assert res != 'abcd', f'{res=} {combination=}'

    def test_single_boschloo(self):
        cc = CachedBoschloo()

        for i in range(50):
            a, b, c, d = (np.random.randint(20) for _ in range(4))

            pval_cache = cc.get_or_create(a, b, c, d)
            res = boschloo_exact([[a, b], [c, d]])
            stat_calc, pval_calc = res.statistic, res.pvalue

            self.assertTrue(np.isclose(pval_cache, min(1., pval_calc)), msg=f'{pval_cache=} != {pval_calc=}; {[[a, b], [c, d]]}')

    def test_many(self):
        cc = CachedBoschloo()

        test_df = pd.DataFrame(
            [(np.random.randint(20) for _ in range(4)) for _ in range(100)],
            columns=['c1r1', 'c2r1', 'c1r2', 'c2r2']
        )

        # create new
        cc.get_or_create_many(test_df)

        # load from cache
        cc.get_or_create_many(test_df)
