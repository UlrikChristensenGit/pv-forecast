import dash_mantine_components as dmc
from dash import Input, Output, callback, html

import components as com


def get_form() -> html.Div:
    return html.Div(
        id="form",
        children=[
            com.Form(
                name="Konfigurering",
                sections=[
                    com.Section(
                        name="Egenskaber",
                        is_open=True,
                        fields=[
                            com.Field(
                                name="Placering",
                                inputs=[
                                    dmc.SegmentedControl(
                                        id="location-type",
                                        value="address",
                                        data=[
                                            {
                                                "value": "address",
                                                "label": "Addresse",
                                            },
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
                                                decimalScale=2,
                                                value=55.36,
                                            ),
                                            dmc.NumberInput(
                                                id="longitude",
                                                placeholder="Longitude",
                                                hideControls=True,
                                                decimalSeparator=".",
                                                decimalScale=2,
                                                value=10.39,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            com.Field(
                                name="Modulkapacitet (DC)",
                                inputs=[
                                    dmc.NumberInput(
                                        id="installed_dc_capacity",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        decimalScale=2,
                                        min=0,
                                        max=1e9,
                                        placeholder=["kW"],
                                        value=100,
                                        fixedDecimalScale=True,
                                    ),
                                ],
                            ),
                            com.Field(
                                name="Inverterkapacitet (AC)",
                                inputs=[
                                    dmc.NumberInput(
                                        id="installed_ac_capacity",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        decimalScale=2,
                                        min=0,
                                        max=1e9,
                                        placeholder=["kW"],
                                        value=90,
                                        fixedDecimalScale=True,
                                    ),
                                ],
                            ),
                            com.Field(
                                name="Hældning (grader fra vandret)",
                                inputs=[
                                    dmc.NumberInput(
                                        id="tilt",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        decimalScale=2,
                                        min=0,
                                        max=90,
                                        placeholder=["Grader"],
                                        value=45,
                                    ),
                                ],
                            ),
                            com.Field(
                                name="Orientering (grader fra nord)",
                                inputs=[
                                    dmc.NumberInput(
                                        id="azimuth",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        decimalScale=2,
                                        min=0,
                                        max=359,
                                        placeholder=["Grader"],
                                        value=180,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    com.Section(
                        name="Avanceret",
                        fields=[
                            com.Field(
                                name="Inverter effektivitet (%)",
                                inputs=[
                                    dmc.NumberInput(
                                        id="inverter_efficiency",
                                        hideControls=True,
                                        decimalSeparator=".",
                                        decimalScale=2,
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
        ],
    )


@callback(
    Output("address", "style"),
    Output("coordinate", "style"),
    Input("location-type", "value"),
)
def show_location_type(location_type: str):
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
