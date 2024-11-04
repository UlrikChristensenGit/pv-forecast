from etl.integrations.dmi import DMIOpenData
from etl.jobs.versioned_nwp import transformations
from sdk import DataLake
import polars as pl
from tempfile import NamedTemporaryFile
from etl.logs import get_logger

logger = get_logger(__name__)


class ETL:

    def __init__(self):
        self.dmi_open_data = DMIOpenData(api_key="ddcc9b1d-9ae0-4693-92f5-ee637c297969")
        self.data_lake = DataLake.from_resource_names(
            storage_account_name="saenigmaarchivedev",
            container_name="analysis",
        )
        self.versioned_nwp_dataset = self._get_versioned_nwp_dataset()

    def _get_versioned_nwp_dataset(self):
        name = "versioned_nwp"

        if self.data_lake.dataset_exists(name):
            return self.data_lake.get_dataset(name)

        return self.data_lake.create_dataset(
            name=name,
            partition_schema={
                "model_run_time_utc": "datetime64[ms]",
                "time_utc": "datetime64[ms]",
            },
        )

    def get_available_forecasts(self) -> pl.DataFrame:
        return self.dmi_open_data.get_collection()

    def get_downloaded_forecasts(self) -> pl.DataFrame:
        return self.versioned_nwp_dataset.get_partition_maps()

    def get_new_forecasts(self) -> pl.DataFrame:
        available_forecasts = self.get_available_forecasts()

        downloaded_forecasts = self.get_downloaded_forecasts()

        if downloaded_forecasts.is_empty():
            new_forecasts = available_forecasts

        else:
            new_forecasts = available_forecasts.join(
                downloaded_forecasts, on=["model_run_time_utc", "time_utc"], how="anti"
            )

        logger.info(
            f"{len(new_forecasts)} new forecasts. {len(available_forecasts)-len(new_forecasts)} existing forecasts."
        )

        return new_forecasts

    def run(self):
        new_forecasts = self.get_new_forecasts()

        for forecast in new_forecasts.iter_rows(named=True):
            logger.info(f"Running ETL for run '{forecast['run_id']}'")

            with NamedTemporaryFile(suffix=".grib") as tmp_download_file:
                self.dmi_open_data.download_run(
                    run_id=forecast["run_id"],
                    file_path=tmp_download_file.name,
                )

                # read temporary file
                ds = transformations.read_grib(tmp_download_file.name)

                ds = transformations.transform_nwp(ds)

                # write to datalake
                self.versioned_nwp_dataset.write(ds)

            logger.info(f"Downloaded {forecast['run_id']}")
