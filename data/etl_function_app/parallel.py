from logic import parsing, transformations, logs, files
from logic.integrations.dmi import DMIOpenData
from logic.integrations.db import LocalDB
from logic.integrations.datalake import DataLake
import polars as pl
from pathlib import Path
import datetime as dt
from tempfile import NamedTemporaryFile
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
import logging
from multiprocessing import Pool, Queue, Manager
logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)


logger = logs.get_logger(__name__)





class Archive:

    def __init__(self):
        datalake_service_client = DataLakeServiceClient(
            account_url="https://saenigmaarchiveprod.dfs.core.windows.net",
            credential=DefaultAzureCredential(),
        )
        self.file_system_client = datalake_service_client.get_file_system_client("landing")


    def get_files(self):
        files = (self.file_system_client.get_paths("forecast_nwp_dmi_harmonie_dini_sf/schema_version=None/year=2024/month=06"))
        files = [file["name"] for file in files if not file["is_directory"]]
        files = sorted(files)
        return files
    
    def download_run(self, run_id: str, destination: Path):
        file_client = self.file_system_client.get_file_client(run_id)
      
        downloader = file_client.download_file()

        with open(destination, "wb") as f:
            for chunk in downloader.chunks():
                f.write(chunk)


class Sandbox:

    def __new__(cls):
        datalake_service_client = DataLakeServiceClient(
            account_url="https://saenigmaarchivedev.dfs.core.windows.net",
            credential=DefaultAzureCredential(),
        )
        directory_client = datalake_service_client.get_directory_client("analysis", "uch/data/nwp")
        return directory_client

def initalize_worker(function):
    function.archive = Archive()
    function.destination = Sandbox()


def log_listener(queue: Queue):
    with open("transformed_files.txt", 'a') as f:
        while 1:
            m = queue.get()
            if m == 'kill':
                f.write('killed')
                break
            f.write(str(m) + '\n')
            f.flush()



def run_for_file(run_id: str, queue: Queue):
    print(run_id)
    with NamedTemporaryFile(suffix=".grib") as temp_file:
        run_for_file.archive.download_run(run_id, temp_file.name)
        ds = transformations.nwp.grib_to_dataset(temp_file.name)
        files.__nwp.dataset_to_netcdf(ds, run_for_file.destination)
    queue.put(run_id)


if __name__ == "__main__":
    archive = Archive()
    run_ids = archive.get_files()

    manager = Manager()
    queue = manager.Queue()
    pool = Pool(initializer=initalize_worker, initargs=(run_for_file,))

    watcher = pool.apply_async(func=log_listener, args=(queue,))

    jobs = []
    for run_id in run_ids:
        job = pool.apply_async(func=run_for_file, args=(run_id, queue))
        jobs.append(job)

    for job in jobs:
        job.get()

    queue.put('kill')
    pool.close()
    pool.join()