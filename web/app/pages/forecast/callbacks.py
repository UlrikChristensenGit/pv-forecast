import datetime as dt
import logging

import numpy as np
import pandas as pd
import plotly.express as px
import xarray as xr
from dash import Input, Output, callback
from plotly import subplots

from app.integrations.dataset import Dataset
from app.simulation.models import (Coordinate, Direction, InverterParameters,
                                   ModuleParameters, System, SystemParameters,
                                   ThermalParameters)
from app.simulation.simulator import Simulator
from cache import cache

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)


def resample_interpolate_center(ds: xr.Dataset, method: str, **indexer_kwargs):
    if len(indexer_kwargs) > 1:
        raise ValueError("Center interpolation only supported along one axis.")

    dim = list(indexer_kwargs.keys())[0]

    start_freq = pd.Timedelta(f"1{xr.infer_freq(ds[dim])}").to_numpy()

    end_freq = np.timedelta64(list(indexer_kwargs.values())[0])

    ds = ds.dropna(dim="time_utc")

    ds = ds.resample(**indexer_kwargs).asfreq()

    ds = ds.interpolate_na(dim=dim, method=method)

    ds[dim] = ds[dim] - start_freq / 2

    return ds


@cache.memoize()
def get_nwp(date_range: tuple[str, str]):
    nwp = Dataset("latest_nwp").read()

    nwp = nwp.sel(
        time_utc=slice(date_range[0], date_range[1]),
        x=slice(1203, 1441),
        y=slice(780, 1027),
    )

    # nwp = nwp.coarsen(x=4, y=4, boundary="trim").mean()

    nwp = nwp.bfill(dim="altitude_m").sel(altitude_m=0)

    nwp = nwp.compute()

    # nwp = resample_interpolate_center(
    #    nwp, method="pchip", time_utc=dt.timedelta(minutes=5)
    # )

    return nwp


sim = Simulator()


@callback(
    Output("forecast-graph", "figure"),
    Input("installed_dc_capacity", "value"),
    Input("installed_ac_capacity", "value"),
    Input("latitude", "value"),
    Input("longitude", "value"),
    Input("tilt", "value"),
    Input("azimuth", "value"),
    Input("inverter_efficiency", "value"),
    Input("date-range", "value"),
)
def display_forecast_graph(
    installed_dc_capacity: float,
    installed_ac_capacity: float,
    latitude: float,
    longitude: float,
    tilt: float,
    azimuth: float,
    inverter_efficiency: float,
    date_range: list[str],
):
    if not installed_dc_capacity or not latitude or not longitude:
        return px.line()

    coord = Coordinate(
        latitude,
        longitude,
        altitude=0,
    )

    direction = Direction(
        azimuth=azimuth,
        elevation=tilt,
    )

    system = System(
        system_params=SystemParameters(
            module_params=ModuleParameters(
                temperature_coefficient=0.004,
                dc_capacity=installed_dc_capacity,
            ),
            inverter_params=InverterParameters(
                nominal_efficiency=inverter_efficiency,
                ac_capacity=installed_ac_capacity,
            ),
            thermal_params=ThermalParameters(
                a=-3.47,
                b=-0.0594,
                deltaT=3,
            ),
        ),
        direction=direction,
        coordinate=coord,
    )

    nwp = get_nwp(date_range)

    result = sim.run(system, nwp)

    df = result.to_dataframe().reset_index()

    df["time_local"] = df["time_utc"].dt.tz_localize("Europe/Copenhagen")

    df = df.rename(
        columns={
            "time_local": "Tid",
            "ac_power": "Produktion [kW]",
            "global_radiation_W_m2": "Global solindstråling [W/m2]",
        }
    )

    fig = subplots.make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("Produktion", "Global solindstråling"),
    )

    power_plot = px.line(
        df,
        x="Tid",
        y=["Produktion [kW]"],
        color_discrete_map={
            "Produktion [kW]": "#d62728",
        },
    )

    nwp_plot = px.line(
        df,
        x="Tid",
        y=["Global solindstråling [W/m2]"],
        color_discrete_map={
            "Global solindstråling [W/m2]": "#bcbd22",
        },
    )

    fig.add_traces(
        data=power_plot.data,
        rows=1,
        cols=1,
    )

    fig.add_traces(
        data=nwp_plot.data,
        rows=2,
        cols=1,
    )

    fig.update_layout(
        {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(255,255,255,0.3)",
            "yaxis": {
                "mirror": True,
                "ticks": "outside",
                "showline": True,
            },
            "xaxis": {
                "mirror": True,
                "ticks": "outside",
                "showline": True,
            },
            "xaxis2_title": "Tid [UTC]",
            "yaxis_title": "[kW]",
            "yaxis2_title": "[W/m2]",
            "margin": {
                "l": 0,
                "r": 0,
                "t": 20,
                "b": 0,
            },
        }
    )

    return fig
