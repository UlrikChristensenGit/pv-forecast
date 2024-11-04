import xarray as xr
from pathlib import Path

GRIB_PROPERTIES = {
    ("temperature", 2): {
        "variable_renaming": {"t2m": "temperature_K"},
        "key_filters": {
            "stepType": "instant",
            "typeOfLevel": "heightAboveGround",
            "parameterCategory": 0,
            "parameterNumber": 0,
            "level": 2,
        },
    },
    ("temperature", 100): {
        "variable_renaming": {"t": "temperature_K"},
        "key_filters": {
            "stepType": "instant",
            "typeOfLevel": "heightAboveGround",
            "parameterCategory": 0,
            "parameterNumber": 0,
            "level": 100,
        },
    },
    ("wind", 10): {
        "variable_renaming": {"u10": "wind_u_m_s", "v10": "wind_v_m_s"},
        "key_filters": {
            "stepType": "instant",
            "typeOfLevel": "heightAboveGround",
            "parameterCategory": 2,
            "parameterNumber": [2, 3],
            "level": 10,
        },
    },
    ("wind", 100): {
        "variable_renaming": {"u100": "wind_u_m_s", "v100": "wind_v_m_s"},
        "key_filters": {
            "stepType": "instant",
            "typeOfLevel": "heightAboveGround",
            "parameterCategory": 2,
            "parameterNumber": [2, 3],
            "level": 100,
        },
    },
    ("radiation", 0): {
        "variable_renaming": {
            "grad": "accumulated_global_radiation_W_m2",
            "nswrf": "accumulated_direct_radiation_W_m2",
        },
        "key_filters": {
            "typeOfLevel": "heightAboveGround",
            "parameterCategory": 4,
            "parameterNumber": [3, 9],
            "level": 0,
        },
    },
}


def grib_param_to_dataset(source: Path, parameter: str, altitude: int) -> xr.Dataset:
    props = GRIB_PROPERTIES[(parameter, altitude)]

    ds = xr.open_dataset(
        source,
        engine="cfgrib",
        backend_kwargs={
            "filter_by_keys": props["key_filters"],
            "indexpath": "",
        },
    )

    ds.attrs["parameter"] = parameter
    ds.attrs["altitude_m"] = altitude

    return ds
