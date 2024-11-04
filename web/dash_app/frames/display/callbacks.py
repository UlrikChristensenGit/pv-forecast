import plotly.express as px
from plotly import subplots
import xarray as xr
import pandas as pd
import numpy as np
import datetime as dt
from dash import Input, Output, callback
from cache import cache

from dash_app.logic.models import (
    Coordinate,
    Direction,
    InverterParameters,
    ModuleParameters,
    System,
    SystemParameters,
    ThermalParameters,
)
from dash_app.logic.simulation.simulator import Simulator


def resample_interpolate_center(ds: xr.Dataset, method: str, **indexer_kwargs):
    if len(indexer_kwargs) > 1:
        raise ValueError("Center interpolation only supported along one axis.")

    dim = list(indexer_kwargs.keys())[0]

    start_freq = pd.Timedelta(f"1{xr.infer_freq(ds[dim])}").to_numpy()

    end_freq = np.timedelta64(list(indexer_kwargs.values())[0])

    ds = ds.copy()

    ds = ds.resample(**indexer_kwargs).asfreq()

    ds = ds.interpolate_na(dim=dim, method=method)

    ds[dim] = ds[dim] - start_freq / 2

    return ds


@cache.memoize()
def get_nwp():
    nwp = xr.open_dataset(
        "/home/uch/PVForecast/_OLD_data/etl_function_app/compressed.nc", engine="h5netcdf"
    )

    nwp = resample_interpolate_center(
        nwp, method="pchip", time_utc=dt.timedelta(minutes=5)
    )

    return nwp


@callback(
    Output("tilt-helper", "children"),
    Input("tilt", "value"),
)
def update_tilt_help(tilt: float):
    if tilt == 0:
        return "Vandret"
    elif tilt == 90:
        return "Lodret"
    else:
        return "Skrå"


@callback(
    Output("azimuth-helper", "children"),
    Input("azimuth", "value"),
)
def update_azimuth_help(azimuth: float):
    if azimuth == 0:
        return "Nord"
    elif azimuth == 90:
        return "Øst"
    elif azimuth == 180:
        return "Syd"
    elif azimuth == 270:
        return "Vest"
    elif 0 < azimuth < 90:
        return "Nord-øst"
    elif 90 < azimuth < 180:
        return "Syd-øst"
    elif 180 < azimuth < 270:
        return "Syd-vest"
    elif 270 < azimuth < 360:
        return "Nord-vest"


@callback(
    Output("graph", "figure"),
    Input("installed_dc_capacity", "value"),
    Input("installed_ac_capacity", "value"),
    Input("latitude", "value"),
    Input("longitude", "value"),
    Input("tilt", "value"),
    Input("azimuth", "value"),
    Input("inverter_efficiency", "value"),
)
def display_graph(
    installed_dc_capacity: float,
    installed_ac_capacity: float,
    latitude: float,
    longitude: float,
    tilt: float,
    azimuth: float,
    inverter_efficiency: float,
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

    sim = Simulator()

    nwp = get_nwp()

    result = sim.run(system, nwp)

    df = result.to_dataframe().reset_index()

    df["time_local"] = df["time_utc"].dt.tz_localize("Europe/Copenhagen")

    df = df.rename(
        columns={
            "time_local": "Tid",
            "ac_power": "Effekt [kW]",
            "global_radiation_W_m2": "Global solindstråling [W/m2]",
        }
    )

    fig = subplots.make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
    )

    power_plot = px.line(
        df,
        x="Tid",
        y=["Effekt [kW]"],
        color_discrete_map={
            "Effekt [kW]": "#d62728",
        }
    )

    nwp_plot = px.line(
        df,
        x="Tid",
        y=["Global solindstråling [W/m2]"],
        color_discrete_map = {
            "Global solindstråling [W/m2]"
        }
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
        }
    )

    return fig


@callback(
    Output("address", "style"),
    Output("coordinate", "style"),
    Input("location-type", "value")
)
def show_location_type_input(location_type: str):
    if location_type == "address":
        return (
            {
                "display": "flex",
                "visibility": "visible",
            }, 
            {
                "display": "none",
                "visibility": "hidden",
            },
        )
    else:
        return (
            {
                "display": "none",
                "visibility": "hidden",
            },
            {
                "display": "flex",
                "visibility": "visible",
            }, 
        )
