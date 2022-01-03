from multiprocessing import Pool
from typing import Optional, Callable

import pandas as pd

from .CachedFunction import CachedFunction


class CachedContingency(CachedFunction):
    function_name: str
    table_name: str
    stat_name: str
    test_function: Callable
    swap_to_string_function: Callable
    swap_series_to_string_function: Callable

    columns = {
        'test': 'text',
        'pval': 'real',
        'stat': 'real'
    }
    pk_col = 'test'

    def __init__(
            self,
            db_path: str = None,
            n_cpus: int = None
    ):
        for attr in ('function_name', 'table_name', 'stat_name', 'columns', 'pk_col',
                     'test_function', 'swap_to_string_function', 'swap_series_to_string_function'):
            assert hasattr(self, attr), f'Failed to build ContingencyCache class: {attr=} is not defined!'

        super().__init__(table_name=self.table_name, db_path=db_path, n_cpus=n_cpus)

    def create_db(self):
        self._create_db(columns=self.columns, pk_col=self.pk_col)

    def get_or_create(self, c1r1: int, c2r1: int, c1r2: int, c2r2: int) -> (float, float):
        test_string = self.swap_to_string_function(c1r1, c2r1, c1r2, c2r2)

        sql = f'SELECT pval, stat FROM {self.table_name} WHERE test = ?'
        res = self.cur.execute(
            sql,
            (test_string,)
        ).fetchone()

        if res is None:
            res = self._create(test_string)

        return res

    def _create(self, test_string: str) -> (float, float):
        pval, stat = self.test_function(test_string)
        self.cur.execute(f'INSERT OR IGNORE INTO {self.table_name} VALUES (?, ?, ?)', (test_string, pval, stat))
        self.con.commit()
        return pval, stat

    def _create_many(self, test_strings: [str]):
        with Pool(self.n_cpus) as p:
            res = p.map(self.test_function, test_strings)

        res = [(test_string, pval, stat) for test_string, (pval, stat) in zip(test_strings, res)]

        self.cur.executemany(
            f'INSERT OR IGNORE INTO {self.table_name} VALUES (?, ?, ?)',
            res
        )
        self.con.commit()

        return pd.DataFrame(res, columns=['__test_string__', 'pval', 'stat'])

    def get_or_create_many(self, test_df: pd.DataFrame, create_only: bool = False) -> Optional[pd.DataFrame]:
        for col in ['c1r1', 'c2r1', 'c1r2', 'c2r2']:
            assert col in test_df.columns, f'Column {col} missing in test_df! {test_df.columns=}'

        test_df['__test_string__'] = test_df.apply(self.swap_series_to_string_function, axis=1)
        unique_tests = test_df['__test_string__'].unique()

        missing = self.cur.execute(
            f'''
            WITH mytable (test) AS ( VALUES {self.list_to_string_bracket(unique_tests)} )
            SELECT test
            FROM mytable
            WHERE NOT EXISTS( SELECT test FROM {self.table_name} WHERE {self.table_name}.test = mytable.test )
            '''

        ).fetchall()

        missing = [m[0] for m in missing]

        self._create_many(missing)

        print(
            f'Calculated {len(missing) / len(unique_tests):.1%} ({len(missing)} out of {len(unique_tests)}) {self.table_name.capitalize()}\'s tests')

        if create_only:
            return

        res = self.cur.execute(
            f'SELECT test, pval, stat FROM {self.table_name} WHERE test IN ({self.list_to_string(unique_tests)})'
        ).fetchall()

        res = pd.DataFrame(data=res, columns=['__test_string__', 'pval', self.stat_name])

        res = pd.merge(test_df, res, on=['__test_string__'], how='left')

        assert len(res) == len(test_df)
        assert (res.__test_string__.values == test_df.__test_string__.values).all()
        res.set_index(test_df.index, inplace=True)

        # undo changes to test_df
        test_df.drop('__test_string__', axis=1, inplace=True)

        assert not any(res.pval.isna()), f'Programming error: Failed to computes some {self.table_name.capitalize()} tests!'

        res.drop('__test_string__', axis=1, inplace=True)

        return res
