import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc, html
from dash_iconify import DashIconify

from pages import forecast


def get_header() -> html.Div:
    return html.Div(
        id="header",
        children=[
            html.H1(
                id="title",
                children="G☀️D S🌤️L · DK",
            ),
        ],
    )


def get_footer() -> html.Div:
    return html.Div(
        id="footer",
        children=[
            DashIconify(
                icon="material-symbols:mail",
                color="#596e79",
            ),
            html.A(
                href="mailto:ulrikchristensen@outlook.com",
                children="ulrikchristensen@outlook.com",
            ),
            DashIconify(
                icon="mdi:linkedin",
                color="#596e79",
            ),
            html.A(
                href="https://www.linkedin.com/in/ulch",
                children="linkedin.com/in/ulch",
            ),
        ],
    )


def get_main() -> html.Div:
    return html.Div(
        id="main",
        children="Main",
    )


def get_layout() -> html.Div:
    """Get layout for forecasts page"""
    return html.Div(
        id="site",
        children=[
            dcc.Location(id="url", refresh=False),
            dmc.ScrollArea(
                id="scroll-area",
                children=[
                    get_header(),
                    get_main(),
                ],
            ),
            get_footer(),
        ],
    )


@callback(
    Output("main", "children"),
    Input("url", "pathname"),
)
def fill_main(pathname: str):
    match pathname:
        case "/":
            return forecast.layout.get_layout()
