import datetime as dt
from pathlib import Path

import xarray as xr


def _get_folder_path_for_date(root: Path, timestamp: dt.date | dt.datetime) -> Path:
    return Path(root) / f"date={timestamp.strftime('%Y-%m-%d')}"


def _get_file_path_for_time(root: Path, timestamp: dt.datetime) -> Path:
    date_folder = _get_folder_path_for_date(root, timestamp)
    file_path = date_folder / f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}.nc"
    return file_path


def _date_range(start: dt.date, end: dt.date) -> list[dt.date]:
    dates = []
    date = start
    while date <= end:
        dates.append(date)
        date = date + dt.timedelta(days=1)
    return dates


def _get_file_paths_for_time_range(
    root, start_time: dt.datetime, end_time: dt.datetime
) -> list[Path]:
    date_range = _date_range(start_time.date(), end_time.date())

    file_paths = []
    for date in date_range:
        date_folder = _get_folder_path_for_date(root, date)
        file_paths += list(date_folder.rglob("*.nc"))

    return file_paths


def _make_nested_list(paths: list[Path]):
    d = dict()
    for path in paths:
        i, j = str(path.name).split("_")
        if j not in d.keys():
            d[j] = []
        d[j].append(str(path))
    return list(d.values())


def _add_dims(ds: xr.Dataset) -> xr.Dataset:
    ds = ds.expand_dims(dim="calculation_time_utc")
    ds = ds.expand_dims(dim="time_utc")
    return ds


def netcdf_to_dataset(source: Path, start_time: dt.datetime, end_time: dt.datetime):
    paths = _get_file_paths_for_time_range(source, start_time, end_time)

    if len(paths) == 0:
        return xr.Dataset()

    # paths = _make_nested_list(paths)

    return xr.open_mfdataset(
        paths, combine="by_coords", engine="h5netcdf", preprocess=_add_dims
    )
