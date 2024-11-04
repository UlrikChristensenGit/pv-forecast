from dash import dcc, html
from dash_app.elements import NavBar, Tab

container = html.Div(
    className="main",
    children=[
        dcc.Location(id="url", refresh=False),
        html.H1(className="title", children="G🌣D S🌣L"),
        NavBar(tabs=[
            Tab(label="Prognose", pathname="forecast"),
            Tab(label="Historisk analyse", pathname="analysis"),
        ]).container,
        html.Div(id="frame"),
    ],
)
