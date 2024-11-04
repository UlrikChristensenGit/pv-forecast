import polars as pl
import datetime as dt
import duckdb
from pathlib import Path
from abc import ABC, abstractmethod


class DB(ABC):

    @abstractmethod
    def read(table_name: str) -> pl.DataFrame:
        pass

    @abstractmethod
    def upsert(df: pl.DataFrame, table_name: str) -> None:
        pass


class LocalDB(DB):

    def __init__(
        self,
        path: str | Path,
    ):
        self.path = Path(path)

    def _get_connection(self):
        filepath = self.path / ".db"

        first = not filepath.exists()

        self.path.mkdir(parents=True, exist_ok=True)

        conn = duckdb.connect(str(filepath))

        if first:
            conn.execute(
                """
            CREATE TABLE nwp_log (
                run_id VARCHAR PRIMARY KEY,
                time_utc TIMESTAMPTZ,
                model_run_time_utc TIMESTAMPTZ,
            );
  
            CREATE TABLE latest_nwp_log (
                model_run_time_utc TIMESTAMPTZ PRIMARY KEY,
            );
            """
            )

        return conn

    def _query(self, query: str, parameters: dict = None) -> pl.DataFrame:
        conn = self._get_connection()

        return conn._query(query).pl()

    def read(self, table_name: str) -> pl.DataFrame:
        conn = self._get_connection()

        query = f"""
        SELECT *
        FROM {table_name}
        """

        return conn.query(query).pl()

    def upsert(self, table_name: str, df: pl.DataFrame) -> None:
        conn = self._get_connection()

        conn.register("df", df)

        query = f"""
        INSERT OR REPLACE INTO {table_name}
        SELECT *
        FROM df
        """

        conn.execute(query)
