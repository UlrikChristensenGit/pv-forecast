import dash_mantine_components as dmc
from dash_app.elements.field import Field


class Section:

    def __init__(
        self,
        name: str,
        fields: list[Field],
        is_open: bool = False,
    ):
        self.name = name
        self.is_open = is_open
        self.container = dmc.AccordionItem(
            className="section",
            value=name,
            children=[
                dmc.AccordionControl(
                    children=name,
                    className="section-header",
                ),
                dmc.AccordionPanel(
                    className="section-body",
                    children=[field.container for field in fields],
                ),
            ],
        )
