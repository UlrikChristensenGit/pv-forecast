from pathlib import Path

import xarray as xr
from xarray import DataArray, Dataset

from dash_app.logic.models import Coordinate, System
from dash_app.logic.simulation import formulas
from dash_app.logic.simulation.kdtree import CoordinateKDTree


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
        self.nwp_kd_tree = self._make_nwp_kd_tree()

    def _make_nwp_kd_tree(self) -> CoordinateKDTree:
        file_path = Path(__file__).parent / "nwp_coordinates.nc"
        coords = xr.open_dataset(file_path, engine="h5netcdf")

        coords = coords.sel(x=slice(1203, 1441), y=slice(780, 1027))

        coords = coords.coarsen(x=4, y=4, boundary="trim").mean()

        kd_tree = CoordinateKDTree()
        kd_tree.fit(coords.coords)

        return kd_tree

    def interpolate_nwp_at_coordinate(
        self, nwp: Dataset, coordinate: Coordinate
    ) -> Dataset:
        nearest_neighbour = self.nwp_kd_tree.nearest_index(coordinate)
        return nwp.sel(nearest_neighbour)

    @staticmethod
    def deaccumulate_radiation(nwp: xr.Dataset) -> xr.Dataset:
        nwp = nwp.copy()
        accum_radiation = nwp[
            ["accumulated_global_radiation_J_m2", "accumulated_direct_radiation_J_m2"]
        ]
        deaccum_radiation = accum_radiation - accum_radiation.shift(time_utc=1)
        nwp[["global_radiation_J_m2", "direct_radiation_J_m2"]] = deaccum_radiation
        nwp = nwp.drop_vars(
            ["accumulated_global_radiation_J_m2", "accumulated_direct_radiation_J_m2"]
        )
        return nwp

    @staticmethod
    def radiation_energy_to_power(nwp: xr.Dataset) -> xr.Dataset:
        nwp = nwp.copy()
        nwp[["global_radiation_W_m2", "direct_radiation_W_m2"]] = nwp[
            ["global_radiation_J_m2", "direct_radiation_J_m2"]
        ] / (60 * 60)
        nwp = nwp.drop_vars(["global_radiation_J_m2", "direct_radiation_J_m2"])
        return nwp

    @staticmethod
    def filter_to_latest_forecast(nwp: xr.Dataset) -> xr.Dataset:
        nwp = nwp.ffill(dim="time_utc")
        nwp = nwp.isel(calculation_time_utc=-1)
        return nwp

    def run(self, system: System, nwp: Dataset) -> Dataset:

        nwp = self.interpolate_nwp_at_coordinate(nwp, system.coordinate)

        ac_power = ac_power_from_nwp(system, nwp)

        ds = nwp.copy()
        ds["ac_power"] = ac_power

        return ds
