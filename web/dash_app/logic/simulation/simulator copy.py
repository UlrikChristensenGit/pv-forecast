import datetime as dt
from pathlib import Path

import xarray as xr
from logic import files
from logic.models import Coordinate, System
from logic.simulation import formulas
from logic.simulation.kdtree import CoordinateKDTree
from xarray import DataArray, Dataset


def ac_power_from_nwp(
    system: System,
    nwp: Dataset,
):
    nwp = nwp.to_dataframe()

    ac_power = formulas.ac_power_from_nwp(system, nwp)

    ac_power = DataArray.from_series(ac_power)

    return ac_power


class Simulator:

    def __init__(self):
        self.storage = Path("/home/uch/PVForecast/data/.data_storage/nwp")
        self.nwp_kd_tree = self._make_nwp_kd_tree()

    def _make_nwp_kd_tree(self) -> CoordinateKDTree:
        file_path = Path(__file__).parent / "nwp_coordinates.nc"
        coords = xr.open_dataset(file_path, engine="h5netcdf")

        kd_tree = CoordinateKDTree()
        kd_tree.fit(coords.coords)

        return kd_tree

    def get_nwp(self, start_time: dt.datetime, end_time: dt.datetime):
        nwp = files.nwp.netcdf_to_dataset(self.storage, start_time, end_time)
        nwp = nwp.sortby(["time_utc", "calculation_time_utc"])
        return nwp

    def interpolate_nwp_along_location(
        self, nwp: Dataset, coordinate: Coordinate
    ) -> Dataset:
        nearest_neighbour = self.nwp_kd_tree.nearest_index(coordinate)
        return nwp.sel(nearest_neighbour)

    @staticmethod
    def add_deaccumulated_radiation(nwp: xr.Dataset) -> xr.Dataset:
        nwp = nwp.copy()
        accum_radiation = nwp[
            ["accumulated_global_radiation_W_m2", "accumulated_direct_radiation_W_m2"]
        ]
        deaccum_radiation = accum_radiation - accum_radiation.shift(time_utc=1)
        nwp[["global_radiation_W_m2", "direct_radiation_W_m2"]] = deaccum_radiation
        return nwp

    @staticmethod
    def radiation_energy_to_power(nwp: xr.Dataset) -> xr.Dataset:
        nwp = nwp.copy()
        nwp[["global_radiation_W_m2", "direct_radiation_W_m2"]] = nwp[
            ["global_radiation_W_m2", "direct_radiation_W_m2"]
        ] / (60 * 60)
        return nwp

    @staticmethod
    def filter_to_latest_forecast(nwp: xr.Dataset) -> xr.Dataset:
        nwp = nwp.ffill(dim="time_utc")
        nwp = nwp.isel(calculation_time_utc=-1)
        return nwp

    def run(
        self, system: System, start_time: dt.datetime, end_time: dt.datetime
    ) -> Dataset:
        nwp = self.get_nwp(start_time, end_time)

        if len(nwp) == 0:
            return xr.Dataset()

        nwp = self.interpolate_nwp_along_location(nwp, system.coordinate)

        nwp = self.add_deaccumulated_radiation(nwp)

        nwp = self.filter_to_latest_forecast(nwp)

        nwp = self.radiation_energy_to_power(nwp)

        ac_power = ac_power_from_nwp(system, nwp)

        ds = nwp.copy()
        ds["ac_power"] = ac_power

        return ds
