import dash_mantine_components as dmc
from dash import html

from app.components.section import Section


class Form:

    def __new__(cls, sections: list[Section]) -> dmc.AccordionMultiple:
        open_section_names = [section.name for section in sections if section.is_open]
        return dmc.AccordionMultiple(
            value=open_section_names,
            className="form",
            children=sections,
        )
