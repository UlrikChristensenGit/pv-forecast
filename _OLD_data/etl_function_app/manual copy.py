from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
from logic import transformations, files
from tempfile import NamedTemporaryFile
from multiprocessing import Pool
import fsspec


sandbox_datalake_service_client = DataLakeServiceClient(
    account_url="https://saenigmaarchivedev.dfs.core.windows.net",
    credential=DefaultAzureCredential(),
)

archive_datalake_service_client = DataLakeServiceClient(
    account_url="https://saenigmaarchiveprod.dfs.core.windows.net",
    credential=DefaultAzureCredential(),
)

file_system_client = archive_datalake_service_client.get_file_system_client("landing")

file_list = file_system_client.get_paths(
    "forecast_nwp_dmi_harmonie_dini_sf/schema_version=None/year=2024/month=06"
)

# destination = sandbox_datalake_service_client.get_directory_client(file_system="analysis", directory="uch/nwp_parquet")

destination = fsspec.filesystem(
    protocol="abfs",
    account_name="saenigmaarchivedev",
    anon=False,
)


def write(file):
    print(f"Writing file {file['name']}")
    file_client = file_system_client.get_file_client(file)

    content = file_client.download_file()

    with NamedTemporaryFile(suffix="grib") as f:
        content.readinto(f)

        ds = transformations.nwp.grib_to_dataset(f.name)

        files.__nwp.dataset_to_delta(ds, destination)


file_list = sorted(file_list, key=lambda file: file["name"])

file_list = [file for file in file_list if not file["is_directory"]]


if __name__ == "__main__":
    with Pool(7) as p:
        print(p.map(write, file_list))
