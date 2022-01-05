from itertools import permutations
import numpy as np
import pandas as pd

# set up logging
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def test_swap(func, expected_combinations: [str], n_swaps=10):
    def is_close(result: list) -> bool:
        assert len(result) == len(ref_result)
        r1_stat, r1_pval = result
        r2_stat, r2_pval = ref_result
        r1_pval = min(1., r1_pval)
        r2_pval = min(1., r2_pval)

        return np.isclose(r1_stat, r2_stat) and np.isclose(r1_pval, r2_pval)

    all_sums = []
    always_identical = None
    for i in range(n_swaps):
        vals = {letter: np.random.randint(20) for letter in 'abcd'}
        res = {
            f'{v1}{v2}{v3}{v4}':
                func([[vals[v1], vals[v2]], [vals[v3], vals[v4]]])
            for v1, v2, v3, v4 in permutations('abcd')
        }
        df = pd.DataFrame(list(res.items()), columns=['test', 'result'])
        df.set_index('test', inplace=True)
        for test, ref_result in res.items():
            df[test] = df['result'].apply(is_close)

        abcd = df['abcd']
        combinations_with_identical_result = set(abcd[abcd].index)

        if always_identical is None:
            always_identical = combinations_with_identical_result
        else:
            always_identical = always_identical.intersection(combinations_with_identical_result)

        all_sums.append(abcd.sum())
        for comb in expected_combinations:
            assert comb in combinations_with_identical_result, \
                f'{comb=} did not yield same result as abcd! {vals=} {combinations_with_identical_result=}'

    assert min(all_sums) == len(expected_combinations), \
        f'Expected always to have at least {len(expected_combinations)} identical combinations. {all_sums} {always_identical=}'


def is_equivalent(a: float, b: float) -> bool:
    if np.isinf(a) and np.isinf(b):
        return True
    if np.isnan(a) and np.isnan(b):
        return True
    return np.isclose(a, b)
