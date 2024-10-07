import logging

from dash import Dash

from dash_app.db import db
from dash_app.frames import home

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "/dash_app/assets/layout.css",
        "/dash_app/assets/typography.css",
    ],
)

app.layout = home.layout.container

if __name__ == "__main__":

    app.run(debug=True)
