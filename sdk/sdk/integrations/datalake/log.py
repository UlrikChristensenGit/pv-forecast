import pandas as pd
import fsspec
import logging

class Log:

    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.fs = fsspec.filesystem(
            protocol="az",
            account_name="sapvforecastuch",
            anon=False,
        )
        self.url = f"az://data/{name}/.csv"
        
    @classmethod
    def create(
        cls,
        name: str,
        schema: dict[str, str],
    ):
        log = cls(name)

        if log.fs.exists(log.url):
            logging.warning("Log already exists. Returning existing object.")
            return log
        
        df = pd.DataFrame(data=[], columns=schema.keys())
        df = df.astype(schema)
        
        df.to_csv(
            path_or_buf=log.url,
            index=False,
            mode="a",
            storage_options=log.fs.storage_options,
        )

        return log

    def write(self, df: pd.DataFrame):
        df.to_csv(
            path_or_buf=self.url,
            index=False,
            mode="a",
            header=False,
            storage_options=self.fs.storage_options,
        )

    def read(self):
        return pd.read_csv(
            filepath_or_buffer=self.url,
            storage_options=self.fs.storage_options,
        )