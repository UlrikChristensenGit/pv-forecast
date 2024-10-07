import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pickle

import xarray as xr

from web.dash_app.logic.simulation.kdtree import CoordinateKDTree

SAMPLE_NWP_FILE = (
    "/home/uch/PVForecast/data/.data_storage/nwp/date=2024-07-28/20240728T150000Z.nc"
)

ds = xr.open_dataset(SAMPLE_NWP_FILE).drop_vars("time_utc")

kdtree = CoordinateKDTree()

kdtree.fit(ds.coords)

with open("logic/simulation/kdtree.pkl", "wb") as f:
    pickle.dump(kdtree, f)
