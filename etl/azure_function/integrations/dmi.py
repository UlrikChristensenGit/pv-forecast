import requests as rq
import pandas as pd
from requests.exceptions import ChunkedEncodingError
from pipeline import retry_policy
import os


BASE_URL = "https://dmigw.govcloud.dk/v1/forecastdata"
MODEL_NAME = "harmonie_dini_sf"


class DMIOpenData:

    def __init__(self):
        self.api_key = os.environ["DMI_OPEN_DATA_API_KEY"]

    def get_collection(self) -> dict:
        response = rq.get(
            url=f"{BASE_URL}/collections/{MODEL_NAME}/items",
            params={"api-key": self.api_key},
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        df = pd.DataFrame(data["features"])

        df = pd.concat([df, pd.json_normalize(df["properties"])], axis="columns")

        for col in ["modelRun", "datetime", "created"]:
            df[col] = df[col].str[:19]
            df[col] = pd.to_datetime(df[col])
            df[col] = df[col].dt.tz_localize(None)
            df[col] = df[col].astype("datetime64[us]")

        df = df.rename(columns={
            "id": "run_id",
            "datetime": "time_utc",
            "modelRun": "model_run_time_utc"
        })

        df["horizon"] = df["time_utc"] - df["model_run_time_utc"]

        df = df.filter([
            "run_id", "model_run_time_utc", "horizon",
        ])

        return df

    @retry_policy(max_retries=3, errors=(ChunkedEncodingError))
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
