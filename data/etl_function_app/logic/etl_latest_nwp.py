from logic import parsing, logs, transformations
from logic.integrations.db import LocalDB
from logic.integrations.datalake import DataLake
import logic.integrations.datalake as dl
import polars as pl
import numpy as np
import xarray as xr
logger = logs.get_logger(__name__)



class ETL:

    def __init__(self):
        self.db = LocalDB(path="/home/uch/PVForecast/data/.log_db")
        self.datalake = DataLake(
            storage_account_name="saenigmaarchivedev",
            container_name="analysis",
        )

    
    def get_available_batches(self) -> pl.DataFrame:
        df = self.db.read("nwp_log")
        
        # only consider batches that are complete
        df = df.filter(pl.count("run_id").over("model_run_time_utc") == 61)

        df = df.unique(subset=["model_run_time_utc"])
               
        return df

    def get_transformed_batches(self) -> pl.DataFrame:
        df = self.db.read("latest_nwp_log")
        
        return df

    def get_new_batches(self) -> pl.DataFrame:
        available_batches = self.get_available_batches()

        transformed_batches = self.get_transformed_batches()

        new_batches = available_batches.join(transformed_batches, on="model_run_time_utc", how="anti")

        logger.info(f"{len(new_batches)} new forecasts. {len(available_batches)-len(new_batches)} existing forecasts.")

        return new_batches


    def log_transformed_batch(self, batch: dict):
        df = pl.DataFrame(data=[{"model_run_time_utc": batch["model_run_time_utc"]}])
        self.db.upsert("latest_nwp_log", df)

    def run(self):
        nwp_dataset = self.datalake.get_dataset("nwp")
        latest_nwp_dataset = self.datalake.create_dataset(
            name="latest_nwp",
            partition_schema={"time_utc": "datetime64"},
        )

        new_batches = (
            self.get_new_batches()
            .sort(by="model_run_time_utc")
        )

        for batch in new_batches.iter_rows(named=True):
            model_run_time_utc = batch["model_run_time_utc"]

            logger.info(f"Running ETL for batch '{model_run_time_utc}'")

            pushdown = (dl.field("model_run_time_utc") == np.datetime64(model_run_time_utc))

            ds = nwp_dataset.read(pushdown)

            ds = transformations.nwp.transform_dataset(ds)

            latest_nwp_dataset.write(ds)

            del ds      

            self.log_transformed_batch(batch)

