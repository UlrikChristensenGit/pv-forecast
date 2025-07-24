import logging
import os

import dash_mantine_components as dmc
import dotenv

dotenv.load_dotenv()

from dash import Dash, _dash_renderer

_dash_renderer._set_react_version("18.2.0")

from pages import home

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=dmc.styles.ALL,
    update_title=False,
)

app.title = "G☀️D S🌤️L · DK"

app.layout = dmc.MantineProvider(home.layout.get_layout())

if __name__ == "__main__":

    # app.server.config["PROFILE"] = True
    # app.server.wsgi_app = ProfilerMiddleware(
    #    app.server.wsgi_app,
    #    sort_by=["cumtime"],
    #    restrictions=[50],
    #    stream=None,
    #    profile_dir=".profile",
    # )
    debug = False
    if "DEBUG" in os.environ:
        if os.environ["DEBUG"] == "1":
            debug = True

    app.run_server(
        host="0.0.0.0",
        port=8050,
        debug=debug,
    )
