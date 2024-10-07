from logic import parsing, logs, transformations
from logic.integrations.dmi import DMIOpenData
from logic.integrations.db import LocalDB
from logic.integrations.datalake import DataLake
import polars as pl
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
from tempfile import NamedTemporaryFile
from io import BytesIO
from requests.exceptions import ChunkedEncodingError

logger = logs.get_logger(__name__)





class ETL:

    def __init__(self):
        self.dmi_open_data = DMIOpenData(api_key="ddcc9b1d-9ae0-4693-92f5-ee637c297969")
        self.db = LocalDB(path="/home/uch/PVForecast/data/.log_db")
        self.data_lake = DataLake(
            storage_account_name="saenigmaarchivedev",
            container_name="analysis",
        )

    
    def get_available_forecasts(self) -> pl.DataFrame:
        data = self.dmi_open_data.get_collection()
        
        df = parsing.collection_to_df(data)
        
        return df

    def get_downloaded_forecasts(self) -> pl.DataFrame:
        df = self.db.read("nwp_log")
        
        return df

    def get_new_forecasts(self) -> pl.DataFrame:
        available_forecasts = self.get_available_forecasts()

        downloaded_forecasts = self.get_downloaded_forecasts()

        new_forecasts = available_forecasts.join(downloaded_forecasts, on="run_id", how="anti")

        logger.info(f"{len(new_forecasts)} new forecasts. {len(available_forecasts)-len(new_forecasts)} existing forecasts.")

        return new_forecasts


    def log_transformed_forecast(self, forecast: dict):
        df = pl.DataFrame(data=[forecast])
        self.db.upsert("nwp_log", df)

    def _download_to_tmp(self, run_id: str, file_path: str):
        # write temporary file
        with self.dmi_open_data.download_run(run_id) as run:
            with open(file_path, "wb") as f:
                for chunk in run.iter_content(chunk_size=8192):
                    f.write(chunk)

    def run(self):
        dataset = self.data_lake.create_dataset(
            name="nwp",
            partition_schema={
                "model_run_time_utc": "datetime64",
                "time_utc": "datetime64",
            }
        )

        new_forecasts = self.get_new_forecasts()

        for forecast in new_forecasts.iter_rows(named=True):
            logger.info(f"Running ETL for run '{forecast['run_id']}'")

            with NamedTemporaryFile(suffix=".grib") as tmp_download_file:
                for i in range(3):
                    try:
                        self._download_to_tmp(
                            run_id=forecast["run_id"],
                            file_path=tmp_download_file.name
                        )
                    except ChunkedEncodingError:
                        logger.warning(f"ChunkedEncodingError on try {i+1}. Retrying...")
                        continue
                    finally:
                        break

                # read temporary file
                ds = transformations.nwp.grib_to_dataset(tmp_download_file.name)

                # write to datalake
                dataset.write(ds)

            self.log_transformed_forecast(forecast)

            logger.info(f"Downloaded {forecast['run_id']}")
