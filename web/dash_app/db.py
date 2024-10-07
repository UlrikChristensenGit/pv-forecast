import polars as pl


class PolarsDB:

    def __init__(self):
        self.storage_options = {
            "account_name": "saenigmaanalysisprod",
            "use_azure_cli": "true",
        }

    def read(self, table_name: str) -> pl.DataFrame:
        return pl.scan_delta(
            f"abfs://delta/live/tables/{table_name}",
            storage_options=self.storage_options,
        )


db = PolarsDB()
