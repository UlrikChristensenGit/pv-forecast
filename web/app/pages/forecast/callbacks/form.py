from dash import Input, Output, callback


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
    Output("address", "style"),
    Output("coordinate", "style"),
    Input("location-type", "value"),
)
def update_location_type_input(location_type: str):
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
