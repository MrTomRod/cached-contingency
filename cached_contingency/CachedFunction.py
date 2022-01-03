import os
import logging
import sqlite3
from typing import Optional
import pandas as pd


class CachedFunction:
    table_name: str

    def __init__(self, table_name, db_path: str = None, n_cpus: int = None):
        self.table_name = table_name

        if db_path is None:
            if 'CACHED_CONTINGENCY_DB' in os.environ:
                db_path = os.environ['CACHED_CONTINGENCY_DB']
            else:
                db_path = os.path.expanduser('~/.cache/contingency.db')

        self.n_cpus = n_cpus if n_cpus else os.cpu_count()
        self._db_path = db_path
        self.con, self.cur = self.get_cur()
        self.create_db()

    def __str__(self):
        return f'FunctionCache {self.table_name} ({self._db_path})'

    def get_cur(self):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        return con, cur

    def __del__(self):
        self.cur.close()
        self.con.close()

    def create_db(self):
        raise NotImplementedError(f'Users of the abstract class {self.__class__} must implement this function!')

    @staticmethod
    def list_to_string(l) -> str:
        return ', '.join(f"'{e}'" for e in l)

    @staticmethod
    def list_to_string_bracket(l):
        return ', '.join(f"('{e}')" for e in l)

    def _create_db(self, columns: {str: str}, pk_col: str):
        columns = ', '.join(f'{col_name} {col_type}' for col_name, col_type in columns.items())
        sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                {columns},
                PRIMARY KEY ({pk_col})
            );
        '''
        try:
            self.cur.execute(sql)
        except sqlite3.OperationalError as e:
            logging.warning(f'Failed to run this SQL command on db {self._db_path}:\n{sql}')
            raise e

    def drop_db(self):
        self.cur.execute(f'''DROP TABLE {self.table_name}''')

    def get_or_create(self, c1r1: int, c2r1: int, c1r2: int, c2r2: int) -> (float, float):
        raise NotImplementedError(f'Users of the abstract class {self.__class__} must implement this function!')

    def _create(self, test_string: str) -> (float, float):
        raise NotImplementedError(f'Users of the abstract class {self.__class__} must implement this function!')

    def _create_many(self, test_strings: [str]):
        raise NotImplementedError(f'Users of the abstract class {self.__class__} must implement this function!')

    def get_or_create_many(self, test_df: pd.DataFrame, create_only: bool = False) -> Optional[pd.DataFrame]:
        raise NotImplementedError(f'Users of the abstract class {self.__class__} must implement this function!')
