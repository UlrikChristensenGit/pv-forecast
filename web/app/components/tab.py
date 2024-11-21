from dash import dcc


class Tab:

    def __new__(self, label: str, pathname: str) -> dcc.Link:
        return dcc.Link(
            className="tab",
            children=label,
            href=pathname,
        )
