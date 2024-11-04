from dash import dcc

class Tab:

    def __init__(self, label: str, pathname: str):
        self.container = dcc.Link(
            className="tab",
            children=label,
            href=pathname,
        )