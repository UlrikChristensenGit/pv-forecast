from etl.integrations.dmi import DMIOpenData
from etl.jobs.latest_nwp import transformations
from sdk import DataLake
import polars as pl
from tempfile import NamedTemporaryFile
from etl.logs import get_logger

logger = get_logger(__name__)


class ETL:

    def __init__(self):
        self.data_lake = DataLake.from_resource_names(
            storage_account_name="saenigmaarchivedev",
            container_name="analysis",
        )
        self.versioned_nwp_dataset = self.data_lake.get_dataset("versioned_nwp")
        self.latest_nwp_dataset = self.data_lake.create_dataset(
            name="latest_nwp",
            partition_schema={
                "time_utc": "datetime64[ms]",
            }
        )

    def get_available_batches(self) -> pl.DataFrame:
        df = self.versioned_nwp_dataset.get_partition_maps()

        # only consider batches that are complete
        df = df.with_columns(pl.count("time_utc").over("model_run_time_utc").alias("cnt"))

        #df = df.filter(pl.col("cnt") == 61)

        df = df.unique(subset=["model_run_time_utc"])

        return df

    def get_transformed_batches(self) -> pl.DataFrame:
        return self.latest_nwp_dataset.get_partition_maps()

    def get_new_batches(self) -> pl.DataFrame:
        available_batches = self.get_available_batches()

        transformed_batches = self.get_transformed_batches()

        if transformed_batches.is_empty:
            new_batches = available_batches

        else:
            new_batches = available_batches.join(
                transformed_batches,
                on=["time_utc"],
                how="anti"
            )

        logger.info(
            f"{len(new_batches)} new batches. {len(available_batches)-len(new_batches)} existing batches."
        )

        return new_batches

    def run(self):
        new_batches = self.get_new_batches()
        
        for batch in new_batches.iter_rows(named=True):

            logger.info(f"Running ETL for batch '{batch['model_run_time_utc']}'")

            pushdown = pl.col("model_run_time_utc") == batch["model_run_time_utc"]

            ds = self.versioned_nwp_dataset.read(pushdown)

            ds = transformations.transform(ds)

            self.latest_nwp_dataset.write(ds)

            logger.info(f"Transformed {batch['model_run_time_utc']}")
