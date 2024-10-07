from dash import dcc, html

container = html.Div(
    className="main",
    children=[
        dcc.Location(id="url", refresh=False),
        html.H1(className="title", children="PV-Prognose"),
        html.Div(id="display-frame"),
    ],
)
