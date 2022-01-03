from unittest import TestCase

from .test_utils import *

from cached_contingency.CachedFisher import CachedFisher, fisher_exact, fisher_swap

FISHER_COMBINATIONS = ['abcd', 'acbd', 'dbca', 'dcba']


class TestCachedFisher(TestCase):
    def test_swap_premise(self):
        test_swap(
            func=lambda table: fisher_exact(table)[0],
            expected_combinations=FISHER_COMBINATIONS
        )

    def test_swap_fisher(self):
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
            pval, stat = cc.get_or_create(a, b, c, d)
            res = fisher_exact([[a, b], [c, d]])

            self.assertTrue(is_equivalent(pval, res[1]))

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
