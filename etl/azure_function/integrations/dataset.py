import numpy as np
import xarray as xr
from zarr.storage import FSStore
import fsspec


class Dataset:

    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.fs = fsspec.filesystem(
            protocol="az",
            account_name="sapvforecastuch",
            anon=False,
        )
        self.remote_store = FSStore(
            url=f"az://data/{name}",
            fs=self.fs,
        )
        self.dims = self._get_dims()


    def _get_dims(self):
        dataset = xr.open_zarr(
            store=self.remote_store,
        )
        dims = list(dataset.dims.keys())
        return dims


    def write(self, dataset: xr.Dataset):
        # make appropiate encodings
        for name in dataset._coord_names:
            if np.issubdtype(dataset[name].dtype, np.datetime64):
                dataset[name].encoding["units"] = "hours since 2024-01-01 00:00:00"
            if np.issubdtype(dataset[name].dtype, np.timedelta64):
                dataset[name].encoding["units"] = "hours"

        region = {dim: "auto" for dim in self.dims}
    
        dataset.to_zarr(
            store=self.remote_store,
            region=region
        )

    def read(self):
        return xr.open_zarr(
            store=self.remote_store,
        )
