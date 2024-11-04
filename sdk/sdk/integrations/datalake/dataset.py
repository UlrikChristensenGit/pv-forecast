import json

import numpy as np
import polars as pl
import xarray as xr
from azure.storage.filedatalake import DataLakeFileClient, FileSystemClient


class Dataset:

    def __init__(
        self,
        name: str,
        file_system_client: FileSystemClient,
    ):
        self.name = name
        self._fs_client = file_system_client
        self.metadata = self._get_metadata()
        self.partition_schema = self.metadata["partition_schema"]

    def _get_metadata(self) -> dict:
        metadata_file = self._fs_client.get_file_client(
            file_path=f"{self.name}/_metadata.json"
        )

        metadata = json.loads(metadata_file.download_file().read())

        return metadata

    def _cast_partition(self, partition: dict) -> dict:
        casted_partition = {}
        for key, value in partition.items():
            dtype = self.partition_schema[key]
            casted_partition[key] = np.array(value).astype(dtype).item()
        return casted_partition

    def _partition_to_file_path(self, partition: dict) -> str:
        casted_partition = self._cast_partition(partition)
        partition_path = "/".join(
            [f"{key}={value}" for key, value in casted_partition.items()]
        )
        path = f"{self.name}/_data/{partition_path}/.nc"
        return path

    def _file_path_to_partition(self, path: str) -> str:
        partition_path = path[len(f"{self.name}/_data/") : -len("/.nc")]
        partition = dict(part.split("=") for part in partition_path.split("/"))
        casted_partition = self._cast_partition(partition)
        return casted_partition

    def _write_path(self, dataset: xr.Dataset, path: str):
        file_client = self._fs_client.get_file_client(path)

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

            partition_path = self._partition_to_file_path(partition)

            self._write_path(partition_dataset, partition_path)

    def _read_path(self, path: str) -> xr.Dataset:
        file_client = self._fs_client.get_file_client(path)

        data = file_client.download_file().read()

        dataset = xr.open_dataset(data)

        return dataset

    def get_partition_maps(self) -> pl.DataFrame:
        paths = self._fs_client.get_paths(path=f"{self.name}/_data", recursive=True)

        paths = [path.name for path in paths if not path.is_directory]

        rows = []
        for path in paths:
            partition = self._file_path_to_partition(path)
            row = partition
            row["path"] = path
            rows.append(row)

        return pl.DataFrame(rows)

    def read(self, pushdown: pl.Expr = None):
        partition_maps = self.get_partition_maps()

        if pushdown is not None:
            partition_maps = partition_maps.filter(pushdown)

        partition_datasets = []
        for partition_map in partition_maps.iter_rows(named=True):
            partition_path = partition_map["path"]
            partition_dataset = self._read_path(partition_path)
            partition_datasets.append(partition_dataset)

        dataset = xr.combine_nested(
            partition_datasets, combine_attrs="drop_conflicts", concat_dim="time_utc"
        )

        return dataset
