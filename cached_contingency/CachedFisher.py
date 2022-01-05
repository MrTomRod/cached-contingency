import pandas as pd
from scipy.stats import fisher_exact

from .CachedContingency import CachedContingency

FISHER_COMBINATIONS = ['abcd', 'acbd', 'badc', 'bdac', 'cadb', 'cdab', 'dbca', 'dcba']


def pickleable_fisher(test_string: str) -> (float, float):
    """
    Calculate Fisher's test

    This function can be pickled

    :param test_string: comma separated contingency table ('1,2,3,4' becomes [[1, 2], [3, 4]])
    :return: Fisher's pvalue, odds ratio
    """
    a, b, c, d = (int(i) for i in test_string.split(','))
    odds_ratio, pvalue = fisher_exact([[a, b], [c, d]])
    return pvalue


def fisher_swap_odds_ratio(a: int, b: int, c: int, d: int) -> (int, int, int, int):
    """
    Four contingency tables always give the same pvalue _and_ odds ratio: ['abcd', 'acbd', 'dbca', 'dcba']

    This is a legacy function.
    """
    if a > d:
        a, d = d, a
    if b > c:
        b, c = c, b
    return a, b, c, d


def fisher_swap(a: int, b: int, c: int, d: int) -> (int, int, int, int):
    """
    Eight contingency tables always give the same pvalue: ['abcd', 'acbd', 'badc', 'bdac', 'cadb', 'cdab', 'dbca', 'dcba']

    Compute and save only one version.
    """
    vals = {'a': a, 'b': b, 'c': c, 'd': d}
    equivalent_combinations = [tuple(vals[letter] for letter in combination) for combination in FISHER_COMBINATIONS]
    return sorted(equivalent_combinations, key=lambda comb: (comb[0], comb[1], comb[2], comb[3]))[0]


def fisher_swap_to_string(a: int, b: int, c: int, d: int) -> str:
    a, b, c, d = fisher_swap(a, b, c, d)
    return f'{a},{b},{c},{d}'


def fisher_swap_series_to_string(data: pd.Series):
    return fisher_swap_to_string(*(data[x] for x in ('c1r1', 'c2r1', 'c1r2', 'c2r2')))


class CachedFisher(CachedContingency):
    function_name = 'fisher'
    table_name = 'fisher'

    def __init__(
            self,
            db_path: str = None,
            n_cpus: int = None
    ):
        self.test_function = pickleable_fisher
        self.swap_function = fisher_swap
        self.swap_to_string_function = fisher_swap_to_string
        self.swap_series_to_string_function = fisher_swap_series_to_string

        super().__init__(
            db_path=db_path,
            n_cpus=n_cpus
        )
