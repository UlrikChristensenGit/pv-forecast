from dash import dcc, html

import app.components as com


def get_layout() -> html.Div:
    return html.Div(
        id="home",
        children=[
            dcc.Location(id="url", refresh=False),
            html.H1(className="title", children="G🌣D S🌣L"),
            com.NavBar(
                tabs=[
                    com.Tab(label="Prognose", pathname="forecast"),
                    com.Tab(label="Historisk analyse", pathname="analysis"),
                ]
            ),
            html.Div(id="home-subpage-frame"),
        ],
    )
