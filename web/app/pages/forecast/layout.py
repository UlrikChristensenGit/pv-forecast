import datetime as dt

import dash_mantine_components as dmc
from dash import dcc, html

import app.components as com


def get_layout() -> html.Div:
    return html.Div(
        id="forecast",
        children=[
            com.Form(
                sections=[
                    com.Section(
                        name="Egenskaber",
                        is_open=True,
                        fields=[
                            com.Field(
                                name="Placering",
                                pickers=[
                                    dmc.SegmentedControl(
                                        id="location-type",
                                        value="address",
                                        data=[
                                            {"value": "address", "label": "Addresse"},
                                            {
                                                "value": "coordinate",
                                                "label": "Koordinat",
                                            },
                                        ],
                                    ),
                                    dmc.Select(
                                        id="address",
                                        className="field",
                                        searchable=True,
                                        initiallyOpened=True,
                                        disabled=True,
                                    ),
                                    html.Div(
                                        id="coordinate",
                                        className="field",
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
                                ],
                            ),
                            com.Field(
                                name="Modulkapacitet (DC)",
                                pickers=[
                                    dmc.NumberInput(
                                        id="installed_dc_capacity",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        precision=2,
                                        min=0,
                                        max=1e9,
                                        placeholder=["kW"],
                                        value=100,
                                    ),
                                ],
                            ),
                            com.Field(
                                name="Inverterkapacitet (AC)",
                                pickers=[
                                    dmc.NumberInput(
                                        id="installed_ac_capacity",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        precision=2,
                                        min=0,
                                        max=1e9,
                                        placeholder=["kW"],
                                        value=90,
                                    ),
                                ],
                            ),
                            com.Field(
                                name="Hældning (grader fra vandret)",
                                pickers=[
                                    dmc.NumberInput(
                                        id="tilt",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        precision=2,
                                        min=0,
                                        max=90,
                                        placeholder=["Grader"],
                                        value=45,
                                    ),
                                ],
                                helper_id="tilt-helper",
                            ),
                            com.Field(
                                name="Orientering (grader fra nord)",
                                pickers=[
                                    dmc.NumberInput(
                                        id="azimuth",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        precision=2,
                                        min=0,
                                        max=359,
                                        placeholder=["Grader"],
                                        value=180,
                                    ),
                                ],
                                helper_id="azimuth-helper",
                            ),
                        ],
                    ),
                    com.Section(
                        name="Avanceret",
                        fields=[
                            com.Field(
                                name="Inverter effektivitet (%)",
                                pickers=[
                                    dmc.NumberInput(
                                        id="inverter_efficiency",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        precision=2,
                                        min=0,
                                        max=1,
                                        placeholder=["%"],
                                        value=0.96,
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
            html.Div(
                id="display",
                children=[
                    html.Div(
                        id="forecast-filters",
                        children=[
                            html.Div(
                                id="date-range-filter",
                                children=[
                                    dmc.DateRangePicker(
                                        id="date-range",
                                        description="Periode",
                                        value=[
                                            dt.datetime.now().date(),
                                            dt.datetime.now().date()
                                            + dt.timedelta(days=1),
                                        ],
                                        allowSingleDateInRange=True,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dcc.Loading(dcc.Graph(id="forecast-graph")),
                ],
            ),
        ],
    )
