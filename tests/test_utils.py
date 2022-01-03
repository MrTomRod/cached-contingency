from itertools import permutations
from math import isnan
import numpy as np
import pandas as pd


def test_swap(func, expected_combinations: [str]):
    all_sums = []
    for i in range(10):
        a, b, c, d = (np.random.randint(20) for i in range(4))
        vals = dict(a=a, b=b, c=c, d=d)
        res = {
            f'{v1}{v2}{v3}{v4}':
                func([[vals[v1], vals[v2]], [vals[v3], vals[v4]]])
            for v1, v2, v3, v4 in permutations('abcd')
        }
        df = pd.DataFrame(list(res.items()), columns=['test', 'pval'])
        df.set_index('test', inplace=True)
        for test, pval in res.items():
            df[test] = np.isclose(df['pval'], pval)

        abcd = df['abcd']
        all_sums.append(abcd.sum())
        for comb in expected_combinations:
            assert comb in abcd[abcd].index, f'{comb=} did not yield same result as abcd! {[a, b, c, d]=}'
    assert min(all_sums) == 4, f'Expected always to have at least 4 identical combinations. {all_sums}'


def is_equivalent(a: float, b: float):
    if isnan(b) or b > 1:
        b = 1.0
    return np.isclose(a, b)
