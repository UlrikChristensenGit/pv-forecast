import datetime as dt

import holoviews as hv
import hvplot.xarray
import pandas as pd
import polars as pl
import xarray as xr
from deltalake import DeltaTable
from holoviews import opts
from logic import files
from logic.models import (
    Coordinate,
    Direction,
    InverterParameters,
    ModuleParameters,
    System,
    SystemParameters,
    ThermalParameters,
)
from logic.simulation.simulator import Simulator

hv.extension("plotly")
pd.options.plotting.backend = "plotly"
hvplot.extension("plotly")

path = "az://analysis/uch/deltalake/nwp"

storage_options = {
    "azure_storage_account_name": "saenigmaarchivedev",
    "use_azure_cli": "True",
}

df = pl.scan_delta(
    source=path,
    storage_options=storage_options,
)

df = df.filter(pl.col("x").is_between(1203, 1441) & pl.col("y").is_between(780, 1027))

print(df.count().collect())
