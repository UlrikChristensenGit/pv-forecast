from dash import Input, Output, callback

from dash_app.frames import display


# CALLBACKS
@callback(
    Output("display-frame", "children"),
    Input("url", "pathname"),
)
def display_frame(pathname: str):
    match pathname:
        case "/display":
            return display.layout.container
