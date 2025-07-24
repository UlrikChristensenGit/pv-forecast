import dash_mantine_components as dmc
from dash import html

from components.section import Section


class Form:

    def __new__(cls, name: str, sections: list[Section]) -> dmc.Accordion:
        open_section_names = [section.name for section in sections if section.is_open]
        return html.Div(
            className="form",
            children=[
                dmc.Accordion(
                    multiple=True,
                    variant="seperated",
                    value=open_section_names,
                    children=sections,
                ),
            ],
        )
