from logic import parsing, logs, transformations
from logic.integrations.dmi import DMIOpenData
from logic.integrations.db import LocalDB
import polars as pl
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
from tempfile import NamedTemporaryFile
from io import BytesIO

logger = logs.get_logger(__name__)


class ETL:

    def __init__(self):
        self.dmi_open_data = DMIOpenData(api_key="ddcc9b1d-9ae0-4693-92f5-ee637c297969")
        self.db = LocalDB(path="/home/uch/PVForecast/data/.log_db")
        self.data_lake = DataLakeServiceClient(
            account_url="https://saenigmaarchivedev.dfs.core.windows.net",
            credential=DefaultAzureCredential(),
        )

    def get_available_forecasts(self) -> pl.DataFrame:
        data = self.dmi_open_data.get_collection()

        df = parsing.dmi.collection_to_df(data)

        # df = transformations.collection.filter_to_latest_run_per_time(df)

        return df

    def get_downloaded_forecasts(self) -> pl.DataFrame:
        df = self.db.read("nwp_log")

        return df

    def get_new_forecasts(self) -> pl.DataFrame:
        available_forecasts = self.get_available_forecasts()

        downloaded_forecasts = self.get_downloaded_forecasts()

        new_forecasts = available_forecasts.join(
            downloaded_forecasts, on="run_id", how="anti"
        )

        logger.info(
            f"{len(new_forecasts)} new forecasts. {len(available_forecasts)-len(new_forecasts)} existing forecasts."
        )

        return new_forecasts

    def log_transformed_forecast(self, forecast: dict):
        df = pl.DataFrame(data=[forecast])
        self.db.upsert("nwp_log", df)

    def run(self):
        fs_client = self.data_lake.get_file_system_client(file_system="analysis")

        new_forecasts = self.get_new_forecasts()

        for forecast in new_forecasts.iter_rows(named=True):
            logger.info(f"Running ETL for run '{forecast['run_id']}'")

            with NamedTemporaryFile(suffix=".grib") as tmp_download_file:
                # write temporary file
                with self.dmi_open_data.download_run(forecast["run_id"]) as run:
                    with open(tmp_download_file.name, "wb") as f:
                        for chunk in run.iter_content(chunk_size=8192):
                            f.write(chunk)

                # read temporary file
                ds = transformations.nwp.grib_to_dataset(tmp_download_file.name)

                model_run_time_utc = forecast["model_run_time_utc"].strftime(
                    "%Y%m%dT%H%M%SZ"
                )
                time_utc = forecast["time_utc"].strftime("%Y%m%dT%H%M%SZ")

                forecast["output_path"] = (
                    f"uch/nwp/model_run_time_utc={model_run_time_utc}/time_utc={time_utc}/{model_run_time_utc}_{time_utc}.nc"
                )

                file_client = fs_client.get_file_client(
                    file_path=forecast["output_path"],
                )

                file_client.upload_data(data=ds.to_netcdf(), overwrite=True)

            self.log_transformed_forecast(forecast)

            logger.info(f"Downloaded {forecast['run_id']}")
