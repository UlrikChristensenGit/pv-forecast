import dash_mantine_components as dmc
from dash import dcc, html, clientside_callback
from dash_app.elements import Form, Section, Field


container = html.Div(
    id="display-page",
    children=[
        Form(
            sections=[

                Section(
                    name="Egenskaber",
                    is_open=True,
                    fields=[
                        Field(
                            name="Placering",
                            pickers=[
                                dmc.SegmentedControl(
                                    id="location-type",
                                    value="address",
                                    data=[
                                        {"value": "address", "label": "Addresse"},
                                        {"value": "coordinate", "label": "Koordinat"},
                                    ],
                                ),
                                dmc.Select(
                                    id="address",
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
                        Field(
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
                        Field(
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
                        Field(
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
                        Field(
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
                Section(
                    name="Avanceret",
                    fields=[
                        Field(
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
        ).container,
        html.Div(className="result", children=[dcc.Loading(dcc.Graph(id="graph"))]),
    ],
)
