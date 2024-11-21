from dash import html

from app.components.tab import Tab


class NavBar:

    def __new__(cls, tabs: list[Tab]) -> html.Div:
        return html.Div(
            className="nav-bar",
            children=tabs,
        )
