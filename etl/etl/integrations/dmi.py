import requests as rq
import polars as pl
from requests.exceptions import ChunkedEncodingError
from etl.pipeline import retry_policy


BASE_URL = "https://dmigw.govcloud.dk/v1/forecastdata"
MODEL_NAME = "harmonie_dini_sf"


class DMIOpenData:

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_collection(self) -> dict:
        response = rq.get(
            url=f"{BASE_URL}/collections/{MODEL_NAME}/items",
            params={"api-key": self.api_key},
        )

        response.raise_for_status()

        data = response.json()

        df = pl.DataFrame(data["features"])

        df = df.unnest("properties")

        df = df.with_columns(
            [
                pl.col(["modelRun", "datetime", "created"]).str.to_datetime().dt.replace_time_zone(None),
            ]
        )

        df = df.select(
            [
                pl.col("id").alias("run_id"),
                pl.col("datetime").alias("time_utc"),
                pl.col("modelRun").alias("model_run_time_utc"),
            ]
        )

        return df

    @retry_policy(max_retries=3, errors=[ChunkedEncodingError])
    def download_run(self, run_id: str, file_path: str):
        with rq.get(
            url=f"{BASE_URL}/download/{run_id}",
            params={"api-key": self.api_key},
            stream=True,
        ) as response:

            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
