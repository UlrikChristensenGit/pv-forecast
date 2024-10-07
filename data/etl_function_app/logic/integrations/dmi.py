import requests as rq
from contextlib import contextmanager


BASE_URL = "https://dmigw.govcloud.dk/v1/forecastdata"
MODEL_NAME = "harmonie_dini_sf"

class DMIOpenData:

    def __init__(
        self,
        api_key: str
    ):
        self.api_key = api_key


    def get_collection(self) -> dict:
        response = rq.get(
            url=f"{BASE_URL}/collections/{MODEL_NAME}/items",
            params={"api-key": self.api_key},
        )

        response.raise_for_status()
        
        data = response.json()

        return data

    @contextmanager
    def download_run(self, run_id: str) -> rq.Response:
        with rq.get(
            url=f"{BASE_URL}/download/{run_id}",
            params={"api-key": self.api_key},
            stream=True,
        ) as response:
            
            response.raise_for_status()

            yield response

    