import dash_mantine_components as dmc

from app.components.field import Field


class Section:

    def __new__(
        self,
        name: str,
        fields: list[Field],
        is_open: bool = False,
    ):
        accordion_item = dmc.AccordionItem(
            className="section",
            value=name,
            children=[
                dmc.AccordionControl(
                    children=name,
                    className="section-header",
                ),
                dmc.AccordionPanel(
                    className="section-body",
                    children=fields,
                ),
            ],
        )
        accordion_item.is_open = is_open
        accordion_item.name = name
        return accordion_item
