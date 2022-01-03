from unittest import TestCase

from .test_utils import *

from cached_contingency.CachedBoschloo import CachedBoschloo, boschloo_exact, boschloo_swap

BOSCHLOO_COMBINATIONS = ['abcd', 'badc', 'cdab', 'dcba']


class TestCachedBoschloo(TestCase):
    def test_swap_premise(self):
        test_swap(
            func=lambda table: boschloo_exact(table).pvalue,
            expected_combinations=BOSCHLOO_COMBINATIONS
        )

    def test_swap_boschloo(self):
        mapper = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        mapper.update({v: k for k, v in mapper.items()})
        map_vals = lambda l: mapper[l]

        for combination in permutations('abcd'):
            combination = ''.join(combination)
            res = ''.join([map_vals(v) for v in boschloo_swap(*[map_vals(l) for l in combination])])

            print(combination, '->', res, combination in BOSCHLOO_COMBINATIONS)
            if combination in BOSCHLOO_COMBINATIONS:
                assert res == 'abcd', f'{res=} {combination=}'
            else:
                assert res != 'abcd', f'{res=} {combination=}'

    def test_single_boschloo(self):
        cc = CachedBoschloo()
        for i in range(100):
            a, b, c, d = (np.random.randint(10) for _ in range(4))
            pval, stat = cc.get_or_create(a, b, c, d)
            res = boschloo_exact([[a, b], [c, d]])

            self.assertTrue(is_equivalent(pval, res.pvalue), f'{[a, b, c, d]=}')

    def test_many(self):
        cc = CachedBoschloo()

        test_df = pd.DataFrame(
            [(np.random.randint(20) for _ in range(4)) for _ in range(20)],
            columns=['c1r1', 'c2r1', 'c1r2', 'c2r2']
        )

        # create new
        cc.get_or_create_many(test_df)

        # load from cache
        return cc.get_or_create_many(test_df)
