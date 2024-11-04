from dash import Input, Output, callback

from dash_app.frames import forecast


# CALLBACKS
@callback(
    Output("frame", "children"),
    Input("url", "pathname"),
)
def display_frame(pathname: str):
    match pathname:
        case "/forecast":
            return forecast.layout.container
