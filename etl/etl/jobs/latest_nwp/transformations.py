import xarray as xr
from logs import get_logger

logger = get_logger(__name__)


def deaccumulate_radiation(ds: xr.Dataset) -> xr.Dataset:
    logger.info("Subtask 1!")
    accum_radiation = ds[
        ["accumulated_global_radiation_J_m2", "accumulated_direct_radiation_J_m2"]
    ]
    logger.info("Subtask 2!")
    logger.info(str(ds["temperature_K"].chunks))
    deaccum_radiation = accum_radiation.diff(dim="time_utc")
    logger.info("Subtask 3!")
    ds = ds.drop_vars(
        ["accumulated_global_radiation_J_m2", "accumulated_direct_radiation_J_m2"]
    )
    logger.info("Subtask 4!")
    ds[["global_radiation_J_m2", "direct_radiation_J_m2"]] = deaccum_radiation

    ds = ds.isel(time_utc=slice(1, len(ds["time_utc"])))

    return ds


def radiation_energy_to_power(ds: xr.Dataset) -> xr.Dataset:
    ds[["global_radiation_W_m2", "direct_radiation_W_m2"]] = ds[
        ["global_radiation_J_m2", "direct_radiation_J_m2"]
    ] / (60 * 60)

    ds = ds.drop_vars(["global_radiation_J_m2", "direct_radiation_J_m2"])

    return ds


def transform(ds: xr.Dataset) -> xr.Dataset:
    logger.info("Task 1")
    ds["time_utc"] = ds["model_run_time_utc"] + ds["horizon"]

    logger.info("Task 2")
    ds = ds.swap_dims(horizon="time_utc")

    logger.info("Task 3")
    ds = ds.drop(["model_run_time_utc", "horizon"])

    logger.info("Task 4")
    ds = deaccumulate_radiation(ds)

    logger.info("Task 5")
    ds = radiation_energy_to_power(ds)

    return ds
