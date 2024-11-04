import dash_mantine_components as dmc
from dash import html
from dash_app.elements.section import Section


class Form:

    def __init__(
        self,
        sections: list[Section],
    ):
        open_section_names = [section.name for section in sections if section.is_open]
        self.container = dmc.AccordionMultiple(
            value=open_section_names,
            className="form",
            children=[section.container for section in sections],
        )
