import xarray as xr

def deaccumulate_radiation(ds: xr.Dataset) -> xr.Dataset:
    accum_radiation = ds[
        ["accumulated_global_radiation_J_m2", "accumulated_direct_radiation_J_m2"]
    ]
    deaccum_radiation = accum_radiation - accum_radiation.shift(time_utc=1)
    ds[["global_radiation_J_m2", "direct_radiation_J_m2"]] = deaccum_radiation
    ds = ds.drop_vars(
        ["accumulated_global_radiation_J_m2", "accumulated_direct_radiation_J_m2"]
    )

    ds = ds.isel(time_utc=slice(1,len(ds["time_utc"])))

    return ds


def radiation_energy_to_power(ds: xr.Dataset) -> xr.Dataset:
    ds = ds.copy()
    ds[["global_radiation_W_m2", "direct_radiation_W_m2"]] = ds[
        ["global_radiation_J_m2", "direct_radiation_J_m2"]
    ] / (60 * 60)

    ds = ds.drop_vars(["global_radiation_J_m2", "direct_radiation_J_m2"])
    
    return ds


def transform(ds: xr.Dataset) -> xr.Dataset:
    ds["time_utc"] = ds["model_run_time_utc"] + ds["horizon"]

    ds = ds.swap_dims(horizon="time_utc")

    ds = ds.drop(["model_run_time_utc", "horizon"])

    ds = deaccumulate_radiation(ds)

    ds = radiation_energy_to_power(ds)

    return ds
