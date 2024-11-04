from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeFileClient,
    DataLakeDirectoryClient,
)
from azure.identity import DefaultAzureCredential
import xarray as xr
import numpy as np
import json
from abc import ABC, abstractmethod
import tqdm


class Rule(ABC):

    def __init__(self, func):
        self.func = func

    def contains(self, partition: dict) -> bool:
        return self.func(partition)

    def __and__(self, other: "Rule") -> "Rule":
        return Rule(
            func=lambda partition: self.func(partition) and other.func(partition)
        )

    def __or__(self, other: "Rule") -> "Rule":
        return Rule(
            func=lambda partition: self.func(partition) or other.func(partition)
        )


ALL = Rule(func=lambda partition: True)


class Field:

    def __init__(self, name: str):
        self.name = name

    def is_between(self, left: object, right: object) -> Rule:
        return Rule(func=lambda partition: left <= partition[self.name] <= right)

    def __eq__(self, other) -> Rule:
        return Rule(func=lambda partition: partition[self.name] == other)

    def __ne__(self, other) -> Rule:
        return Rule(func=lambda partition: partition[self.name] != other)

    def __lt__(self, other) -> Rule:
        return Rule(func=lambda partition: partition[self.name] < other)

    def __le__(self, other) -> Rule:
        return Rule(func=lambda partition: partition[self.name] <= other)

    def __gt__(self, other) -> Rule:
        return Rule(func=lambda partition: partition[self.name] > other)

    def __ge__(self, other) -> Rule:
        return Rule(func=lambda partition: partition[self.name] >= other)

    def __contains__(self, other) -> Rule:
        return Rule(func=lambda partition: other in partition[self.name])


def field(name: str):
    return Field(name)


class Dataset:

    def __init__(
        self,
        datalake: "DataLake",
        name: str,
    ):
        self.name = name
        self.datalake = datalake
        self.metadata = self._get_metadata()
        self.partition_schema = self.metadata["partition_schema"]

    def _get_metadata(self) -> dict:
        metadata_file = self.datalake._get_dataset_metadata_file_client(self.name)

        metadata = json.loads(metadata_file.download_file().read())

        return metadata

    def _partition_to_file_path(self, partition: dict) -> str:
        casted_partition = self._cast_partition(partition)
        partition_path = "/".join(
            [f"{key}={value}" for key, value in casted_partition.items()]
        )
        path = f"{self.name}/_data/{partition_path}/.nc"
        return path

    def _cast_partition(self, partition: dict) -> dict:
        casted_partition = {}
        for key, value in partition.items():
            dtype = self.partition_schema[key]
            casted_partition[key] = np.array(value).astype(dtype)
        return casted_partition

    def _file_path_to_partition(self, path: str) -> str:
        partition_path = path[len(f"{self.name}/_data/") : -len("/.nc")]
        partition = dict(part.split("=") for part in partition_path.split("/"))
        casted_partition = self._cast_partition(partition)
        return casted_partition

    def _get_partition_file_client(self, partition: dict) -> DataLakeFileClient:
        path = self._partition_to_file_path(partition)

        file_client = self.datalake._fs_client.get_file_client(path)

        return file_client

    def _write_partition(self, dataset: xr.Dataset, partition: dict):
        file_client = self._get_partition_file_client(partition)

        data = dataset.to_netcdf()

        file_client.upload_data(data, overwrite=True)

    def write(self, dataset: xr.Dataset):
        partition_keys = list(self.partition_schema.keys())

        stacked_dataset = dataset.stack(partition=partition_keys)

        for partition_values, stacked_partition_dataset in stacked_dataset.groupby(
            "partition"
        ):
            partition_dataset = stacked_partition_dataset.unstack("partition")

            partition = dict(zip(partition_keys, partition_values))
            self._write_partition(partition_dataset, partition)

    def _read_path(self, path: str) -> xr.Dataset:
        file_client = self.datalake._fs_client.get_file_client(path)

        data = file_client.download_file().read()

        dataset = xr.open_dataset(data)

        return dataset

    def _list_paths(self) -> list[str]:
        files = self.datalake._fs_client.get_paths(
            path=f"{self.name}/_data", recursive=True
        )
        return [file.name for file in files if not file.is_directory]

    def _yield_datasets(self, pushdown: Rule = ALL):
        valid_paths = [
            path
            for path in self._list_paths()
            if pushdown.contains(self._file_path_to_partition(path))
        ]

        for path in tqdm.tqdm(valid_paths):
            yield self._read_path(path)

    def read(self, pushdown: Rule = ALL):
        datasets = list(self._yield_datasets(pushdown))

        return xr.combine_nested(
            datasets, combine_attrs="drop_conflicts", concat_dim="time_utc"
        )


class DataLake:

    def __init__(self, storage_account_name: str, container_name: str):
        self._dls_client = DataLakeServiceClient(
            account_url=f"https://{storage_account_name}.dfs.core.windows.net",
            credential=DefaultAzureCredential(),
        )
        self._fs_client = self._dls_client.get_file_system_client(
            file_system=container_name
        )

    def list_datasets(self) -> list[str]:
        datasets = self._fs_client.get_paths()
        return [dataset.name for dataset in datasets if dataset.is_directory]

    def _raise_if_dataset_does_not_exist(self, name: str):
        if not self.dataset_exists(name):
            raise ValueError(f"Dataset `{name}` does not exist.")

    def get_dataset(self, name: str) -> Dataset:
        self._raise_if_dataset_does_not_exist(name)

        return Dataset(self, name)

    def delete_dataset(self, name: str, prompt_user: bool = True) -> None:
        self._raise_if_dataset_does_not_exist(name)

        if prompt_user:
            answer = input(f"Are you sure you want to delete dataset `{name}`? [y/n] ")
            if answer.lower() != "y":
                raise ValueError("Deletion aborted by user.")

        self._fs_client.delete_directory(directory=name)

    def dataset_exists(self, name: str) -> bool:
        return self._fs_client.get_directory_client(name).exists()

    def _get_dataset_metadata_file_client(self, name) -> DataLakeFileClient:
        return self._fs_client.get_file_client(file_path=f"{name}/_metadata.json")

    def create_dataset(
        self,
        name: str,
        partition_schema: dict = None,
        overwrite: bool = False,
        promp_user: bool = True,
    ) -> Dataset:
        if self.dataset_exists(name):
            if overwrite:
                self.delete_dataset(name, prompt_user=promp_user)
            else:
                return self.get_dataset(name)

        if partition_schema is None:
            partition_schema = {}

        metadata = {
            "partition_schema": partition_schema,
        }

        metadata_file = self._get_dataset_metadata_file_client(name)

        metadata_file.upload_data(
            data=json.dumps(metadata),
            overwrite=True,
        )

        return Dataset(self, name)
