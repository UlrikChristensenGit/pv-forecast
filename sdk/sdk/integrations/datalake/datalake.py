import json

from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient, FileSystemClient, DataLakeDirectoryClient

from sdk.integrations.datalake.dataset import Dataset


class DataLake:

    def __init__(self, file_system_client: FileSystemClient):
        self._fs_client = file_system_client

    @classmethod
    def from_resource_names(
        cls,
        storage_account_name: str,
        container_name: str,
    ):
        dls_client = DataLakeServiceClient(
            account_url=f"https://{storage_account_name}.dfs.core.windows.net",
            credential=DefaultAzureCredential(),
        )

        fs_client = dls_client.get_file_system_client(file_system=container_name)

        return cls(fs_client)

    def list_datasets(self) -> list[str]:
        datasets = self._fs_client.get_paths()
        return [dataset.name for dataset in datasets if dataset.is_directory]

    def _raise_if_dataset_does_not_exist(self, name: str):
        if not self.dataset_exists(name):
            raise ValueError(f"Dataset `{name}` does not exist.")

    def get_dataset(self, name: str) -> Dataset:
        self._raise_if_dataset_does_not_exist(name)

        return Dataset(name, self._fs_client)

    def delete_dataset(self, name: str, prompt_user: bool = True) -> None:
        self._raise_if_dataset_does_not_exist(name)

        if prompt_user:
            answer = input(f"Are you sure you want to delete dataset `{name}`? [y/n] ")
            if answer.lower() != "y":
                raise ValueError("Deletion aborted by user.")

        self._fs_client.delete_directory(directory=name)

    def dataset_exists(self, name: str) -> bool:
        return self._fs_client.get_directory_client(name).exists()

    def create_dataset(
        self,
        name: str,
        partition_schema: dict = None,
        overwrite: bool = False,
        prompt_user: bool = True,
    ) -> Dataset:
        if self.dataset_exists(name):
            if overwrite:
                self.delete_dataset(name, prompt_user=prompt_user)
            else:
                return self.get_dataset(name)

        if partition_schema is None:
            partition_schema = {}

        metadata = {
            "partition_schema": partition_schema,
        }

        metadata_file = self._fs_client.get_file_client(
            file_path=f"{name}/_metadata.json"
        )

        metadata_file.upload_data(
            data=json.dumps(metadata),
            overwrite=True,
        )

        data_folder = self._fs_client.get_directory_client(
            directory=f"{name}/_data"
        )

        data_folder.create_directory()

        return Dataset(name, self._fs_client)
