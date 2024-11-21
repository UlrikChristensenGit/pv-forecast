import logging

import dotenv
from werkzeug.middleware.profiler import ProfilerMiddleware

dotenv.load_dotenv()

from dash import Dash

from app.pages import home

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
)

app.layout = home.layout.get_layout()

if __name__ == "__main__":

    app.server.config["PROFILE"] = True
    app.server.wsgi_app = ProfilerMiddleware(
        app.server.wsgi_app,
        sort_by=["cumtime"],
        restrictions=[50],
        stream=None,
        profile_dir=".profile",
    )
    app.run(debug=True)
