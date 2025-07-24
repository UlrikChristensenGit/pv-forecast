import datetime as dt
import logging

import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html
import dash
from dash_iconify import DashIconify
from plotly import subplots

from cache import cache
from integrations.dataset import Dataset
from simulation.models import (Coordinate, Direction, InverterParameters,
                               ModuleParameters, System, SystemParameters,
                               ThermalParameters)
from simulation.simulator import Simulator

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)


def get_filters() -> html.Div:
    return html.Div(
        id="filters",
        className="bar",
        children=[
            html.Div(
                id="display-format-filter",
                className="filter",
                children=[
                    html.P("Format"),
                    dmc.SegmentedControl(
                        id="display-format",
                        value="graph",
                        data=[
                            {"value": "graph", "label": "Graf"},
                            {"value": "table", "label": "Tabel"},
                        ],
                    ),
                ],
            ),
            html.Div(
                id="copy-url-filter",
                className="filter",
                children=[
                    html.P("Kopier link"),
                    dmc.Button(
                        id="copy-url",
                        children=DashIconify(icon="ic:baseline-content-copy"),
                    ),
                ],
            ),
            html.Div(
                id="date-range-filter",
                className="filter",
                children=[
                    html.P("Periode"),
                    dmc.DatePickerInput(
                        id="date-range",
                        type="range",
                        valueFormat="MMM D, YYYY",
                        value=[
                            dt.datetime.now().date(),
                            dt.datetime.now().date() + dt.timedelta(days=2),
                        ],
                        allowSingleDateInRange=True,
                    ),
                ],
            ),
        ],
    )


def get_visualization() -> html.Div:
    return html.Div(
        id="visualization",
        children=[
            dcc.Loading(dcc.Graph(id="time-series-graph"), delay_show=2000),
            dcc.Loading(dmc.ScrollArea(id="time-series-table"), delay_show=2000),
        ],
    )


@callback(
    Output("time-series-graph", "style"),
    Output("time-series-table", "style"),
    Input("display-format", "value"),
)
def hide_or_show_display_format(display_format: str):
    match display_format:
        case "graph":
            return {"display": "block"}, {"display": "none"}
        case "table":
            return {"display": "none"}, {"display": "block"}


def get_results() -> html.Div:
    return html.Div(
        id="results",
        children=[
            dcc.Clipboard(id="clipboard", style={"display": "none"}),
            get_filters(),
            get_visualization(),
        ],
    )


@cache.memoize()
def get_nwp(date_range: tuple[str, str]):
    nwp = Dataset("latest_nwp").read()

    start_time = dt.datetime.fromisoformat(date_range[0])
    end_time = dt.datetime.fromisoformat(date_range[1])

    nwp = nwp.sel(
        time_utc=slice(start_time, end_time),
        x=slice(1203, 1441),
        y=slice(780, 1027),
    )

    nwp = nwp.bfill(dim="altitude_m").sel(altitude_m=0)

    nwp = nwp.compute()

    return nwp


sim = Simulator()


def make_figure(df: pd.DataFrame):
    fig = subplots.make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
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
        y=["Global solindstråling [W/m²]"],
        color_discrete_map={
            "Global solindstråling [W/m²]": "#bcbd22",
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
            "yaxis2_title": "[W/m²]",
            "margin": {
                "l": 0,
                "r": 0,
                "t": 20,
                "b": 0,
            },
        }
    )

    return fig


def make_table(df: pd.DataFrame):
    df = df.round(2)

    table = dmc.ScrollArea(
        children=[dmc.Table(data={"head": df.columns, "body": df.values.tolist()})]
    )
    return table


@callback(
    Output("time-series-graph", "figure"),
    Output("time-series-table", "children"),
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
    if not all([installed_dc_capacity, installed_ac_capacity, latitude, longitude, tilt, azimuth, inverter_efficiency]):
        return dash.no_update

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

    df = df.filter(
        [
            "time_local",
            "ac_power",
            "global_radiation_W_m2",
        ]
    )

    df = df.rename(
        columns={
            "time_local": "Tid",
            "ac_power": "Produktion [kW]",
            "global_radiation_W_m2": "Global solindstråling [W/m²]",
        }
    )

    fig = make_figure(df)

    table = make_table(df)

    return fig, table
