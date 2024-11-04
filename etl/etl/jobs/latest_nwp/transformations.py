import xarray as xr

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
