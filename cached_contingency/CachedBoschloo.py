import pandas as pd
from scipy.stats import boschloo_exact

from .CachedContingency import CachedContingency


def pickleable_boschloo(test_string: str) -> (float, float):
    """
    Calculate Boschloo's test, ensure that pvalue and stat are never nan

    This function can be pickled

    :param test_string: comma separated contingency table ('1,2,3,4' becomes [[1, 2], [3, 4]])
    :return: Boschloo's pvalue, Fisher's pvalue
    """
    c1r1, c2r1, c1r2, c2r2 = (int(i) for i in test_string.split(','))
    boschloo_res = boschloo_exact([[c1r1, c2r1], [c1r2, c2r2]])

    # enforce pvalue and statistic <= 1
    return min(1, boschloo_res.pvalue), min(1, boschloo_res.statistic)


def boschloo_swap(c1r1: int, c2r1: int, c1r2: int, c2r2: int) -> (int, int, int, int):
    """
    Four contingency tables always give the same result: ['abcd', 'badc', 'cdab', 'dcba']

    Compute and save only one version.
    """
    if c1r1 + c1r2 > c2r1 + c2r2:  # left > right
        c1r1, c1r2, c2r1, c2r2 = c2r1, c2r2, c1r1, c1r2
    if c1r1 + c2r1 > c1r2 + c2r2:  # left > right
        c1r1, c2r1, c1r2, c2r2 = c1r2, c2r2, c1r1, c2r1
    return c1r1, c2r1, c1r2, c2r2


def boschloo_swap_to_string(c1r1: int, c2r1: int, c1r2: int, c2r2: int) -> str:
    c1r1, c2r1, c1r2, c2r2 = boschloo_swap(c1r1, c2r1, c1r2, c2r2)
    return f'{c2r1},{c1r1},{c2r2},{c1r2}'


def boschloo_swap_series_to_string(data: pd.Series) -> str:
    return boschloo_swap_to_string(data['c1r1'], data['c2r1'], data['c1r2'], data['c2r2'])


class CachedBoschloo(CachedContingency):
    function_name = 'boschloo'
    table_name = 'boschloo'
    stat_name = 'fisher_stat'

    def __init__(
            self,
            db_path: str = None,
            n_cpus: int = None
    ):
        self.test_function = pickleable_boschloo
        self.swap_function = boschloo_swap
        self.swap_to_string_function = boschloo_swap_to_string
        self.swap_series_to_string_function = boschloo_swap_series_to_string

        super().__init__(
            db_path=db_path,
            n_cpus=n_cpus
        )
