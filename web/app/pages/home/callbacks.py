from dash import Input, Output, callback

from app.pages import forecast


@callback(
    Output("home-subpage-frame", "children"),
    Input("url", "pathname"),
)
def display_frame(pathname: str):
    match pathname:
        case "/forecast":
            return forecast.layout.get_layout()
