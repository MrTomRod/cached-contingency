import pandas as pd
from scipy.stats import fisher_exact

from .CachedContingency import CachedContingency


def pickleable_fisher(test_string: str) -> (float, float):
    """
    Calculate Fisher's test

    This function can be pickled

    :param test_string: comma separated contingency table ('1,2,3,4' becomes [[1, 2], [3, 4]])
    :return: Fisher's pvalue, odds ratio
    """
    c1r1, c2r1, c1r2, c2r2 = (int(i) for i in test_string.split(','))
    odds_ratio, pvalue = fisher_exact([[c1r1, c2r1], [c1r2, c2r2]])
    return pvalue, odds_ratio


def fisher_swap(c1r1: int, c2r1: int, c1r2: int, c2r2: int) -> (int, int, int, int):
    """
    Four contingency tables always give the same result: ['abcd', 'acbd', 'dbca', 'dcba']

    Compute and save only one version.
    """
    if c1r1 > c2r2:
        c1r1, c2r2 = c2r2, c1r1
    if c2r1 > c1r2:
        c2r1, c1r2 = c1r2, c2r1
    return c1r1, c2r1, c1r2, c2r2


def fisher_swap_to_string(c1r1: int, c2r1: int, c1r2: int, c2r2: int) -> str:
    c1r1, c2r1, c1r2, c2r2 = fisher_swap(c1r1, c2r1, c1r2, c2r2)
    return f'{c2r1},{c1r1},{c2r2},{c1r2}'


def fisher_swap_series_to_string(data: pd.Series):
    return fisher_swap_to_string(*(data[x] for x in ('c1r1', 'c2r1', 'c1r2', 'c2r2')))


class CachedFisher(CachedContingency):
    function_name = 'fisher'
    table_name = 'fisher'
    stat_name = 'odds_ratio'

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
