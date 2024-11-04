from logic import parsing
from pathlib import Path
import xarray as xr

KEY_FILTERS = {
    ("temperature", 2): {
        "stepType": "instant",
        "typeOfLevel": "heightAboveGround",
        "parameterCategory": 0,
        "parameterNumber": 0,
        "level": 2,
    },
    ("temperature", 100): {
        "stepType": "instant",
        "typeOfLevel": "heightAboveGround",
        "parameterCategory": 0,
        "parameterNumber": 0,
        "level": 100,
    },
    ("wind", 10): {
        "stepType": "instant",
        "typeOfLevel": "heightAboveGround",
        "parameterCategory": 2,
        "parameterNumber": [2, 3],
        "level": 10,
    },
    ("wind", 100): {
        "stepType": "instant",
        "typeOfLevel": "heightAboveGround",
        "parameterCategory": 2,
        "parameterNumber": [2, 3],
        "level": 100,
    },
    ("radiation", 0): {
        "typeOfLevel": "heightAboveGround",
        "parameterCategory": 4,
        "parameterNumber": [3, 9],
        "level": 0,
    },
}

VARIABLE_RENAMINGS = {
    ("temperature", 2): {"t2m": "temperature_K"},
    ("temperature", 100): {"t": "temperature_K"},
    ("wind", 10): {"u10": "wind_u_m_s", "v10": "wind_v_m_s"},
    ("wind", 100): {"u100": "wind_u_m_s", "v100": "wind_v_m_s"},
    ("radiation", 0): {
        "grad": "accumulated_global_radiation_W_m2",
        "nswrf": "accumulated_direct_radiation_W_m2",
    },
}

USED_KEYS = [("temperature", 2), ("wind", 10), ("radiation", 0)]


def rename_variables(ds: xr.Dataset, parameter: str, altitude: int) -> xr.Dataset:
    variable_renamings = VARIABLE_RENAMINGS[parameter, altitude]
    return ds.rename(variable_renamings).rename(
        {
            "heightAboveGround": "altitude_m",
            "valid_time": "time_utc",
            "time": "model_run_time_utc",
        }
    )


def remove_altitude(ds: xr.Dataset) -> xr.Dataset:
    ds = ds.drop_vars("altitude_m")
    del ds.attrs["altitude_m"]
    return ds


def grib_to_dataset(source: Path) -> xr.Dataset:
    ds_params = []
    for parameter, altitude in USED_KEYS:
        ds_param = parsing.grib_param_to_dataset(source, parameter, altitude)
        ds_param = rename_variables(ds_param, parameter, altitude)
        ds_param = remove_altitude(ds_param)
        ds_params.append(ds_param)
    ds = xr.merge(ds_params)

    ds = ds.set_coords(["latitude", "longitude"])

    ds = ds.drop_vars(["number", "step"])

    ds = ds.expand_dims(["time_utc", "model_run_time_utc"])

    return ds


def deaccumulate_radiation(ds: xr.Dataset) -> xr.Dataset:
    ds = ds.copy()
    accum_radiation = ds[
        ["accumulated_global_radiation_W_m2", "accumulated_direct_radiation_W_m2"]
    ]
    deaccum_radiation = accum_radiation - accum_radiation.shift(time_utc=1)
    ds[["global_radiation_J_m2", "direct_radiation_J_m2"]] = deaccum_radiation
    ds = ds.drop_vars(
        ["accumulated_global_radiation_W_m2", "accumulated_direct_radiation_W_m2"]
    )
    ds = ds.dropna(dim="time_utc")
    return ds


def radiation_energy_to_power(ds: xr.Dataset) -> xr.Dataset:
    ds = ds.copy()
    ds[["global_radiation_W_m2", "direct_radiation_W_m2"]] = ds[
        ["global_radiation_J_m2", "direct_radiation_J_m2"]
    ] / (60 * 60)
    ds = ds.drop_vars(["global_radiation_J_m2", "direct_radiation_J_m2"])
    return ds


def transform(ds: xr.Dataset) -> xr.Dataset:
    ds = deaccumulate_radiation(ds)

    ds = radiation_energy_to_power(ds)

    ds = ds.isel(model_run_time_utc=0)

    return ds
