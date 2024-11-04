from functools import lru_cache

import dash_mantine_components as dmc
import plotly.express as px
import polars as pl
import xarray as xr
from dash import Input, Output, callback, dcc, html

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


def field(
    name: str,
    picker: html.Div,
    helper_id: str = None,
    description: str = None,
):
    picker_group_children = [
        html.Div(className="picker", children=[picker]),
    ]
    if helper_id:
        picker_group_children.append(
            html.Div(
                className="helper",
                id=helper_id,
            )
        )
    children = [
        html.Div(
            className="name",
            children=name,
        ),
        html.Div(className="picker-group", children=picker_group_children),
    ]

    if description:
        children.insert(
            1,
            html.Div(
                className="description",
                children=description,
            ),
        )
    return html.Div(
        className="field",
        children=children,
    )


def section(name: str, fields: list[html.Div]):
    return dmc.AccordionItem(
        className="accordion-item",
        value=name,
        children=[
            dmc.AccordionControl(name, className="accordion-control"),
            dmc.AccordionPanel(
                children=fields,
            ),
        ],
    )


layout = html.Div(
    id="create-page",
    children=[
        dmc.AccordionMultiple(
            value=["Egenskaber"],
            className="form",
            children=[
                section(
                    name="Egenskaber",
                    fields=[
                        field(
                            name="Placering",
                            picker=html.Div(
                                className="location-picker",
                                children=[
                                    dmc.NumberInput(
                                        id="latitude",
                                        placeholder="Latitude",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        precision=2,
                                        value=55.36,
                                    ),
                                    dmc.NumberInput(
                                        id="longitude",
                                        placeholder="Longitude",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        precision=2,
                                        value=10.39,
                                    ),
                                ],
                            ),
                        ),
                        field(
                            name="Modulkapacitet (DC)",
                            picker=dmc.NumberInput(
                                id="installed_dc_capacity",
                                hideControls=True,
                                decimalSeparator=".",
                                precision=2,
                                min=0,
                                max=1e9,
                                placeholder=["kW"],
                                value=100,
                            ),
                        ),
                        field(
                            name="Inverterkapacitet (AC)",
                            picker=dmc.NumberInput(
                                id="installed_ac_capacity",
                                hideControls=True,
                                decimalSeparator=".",
                                precision=2,
                                min=0,
                                max=1e9,
                                placeholder=["kW"],
                                value=90,
                            ),
                        ),
                        field(
                            name="Hældning (grader fra vandret)",
                            picker=dmc.NumberInput(
                                id="tilt",
                                hideControls=True,
                                decimalSeparator=".",
                                precision=2,
                                min=0,
                                max=90,
                                placeholder=["Grader"],
                                value=45,
                            ),
                            helper_id="tilt-help",
                        ),
                        field(
                            name="Orientering (grader fra nord)",
                            picker=dmc.NumberInput(
                                id="azimuth",
                                hideControls=True,
                                decimalSeparator=".",
                                precision=2,
                                min=0,
                                max=359,
                                placeholder=["Grader"],
                                value=180,
                            ),
                            helper_id="azimuth-help",
                        ),
                    ],
                ),
                section(name="Avanceret", fields=[]),
            ],
        ),
        html.Div(className="result", children=[dcc.Loading(dcc.Graph(id="graph"))]),
    ],
)


@lru_cache()
def get_nwp():
    nwp = xr.open_dataset(
        "/home/uch/PVForecast/data/etl_function_app/compressed.nc", engine="h5netcdf"
    )
    return nwp


@callback(
    Output("tilt-help", "children"),
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
    Output("azimuth-help", "children"),
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
)
def display_graph(
    installed_dc_capacity: float,
    installed_ac_capacity: float,
    latitude: float,
    longitude: float,
    tilt: float,
    azimuth: float,
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
                nominal_efficiency=0.96,
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

    plot = px.line(
        df,
        x="time_utc",
        y="ac_power",
    )

    fig = plot.update_layout(
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
            "xaxis_title": "Tid [UTC]",
            "yaxis_title": "Effekt [kW]",
        }
    )

    return fig
