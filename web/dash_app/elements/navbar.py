from dash_app.elements.tab import Tab
from dash import html

class NavBar:

    def __init__(self, tabs: list[Tab]):
        self.container = html.Div(
            className="nav-bar",
            children=[tab.container for tab in tabs]
        )