from dash import html


class Field:

    def __new__(
        cls,
        name: str,
        inputs: list[html.Div],
    ) -> html.Div:
        field_body_children = [
            html.Div(
                className="field-inputs",
                children=inputs,
            ),
        ]

        field_children = [
            html.Div(
                className="field-header",
                children=name,
            ),
            html.Div(
                className="field-body",
                children=field_body_children,
            ),
        ]

        div = html.Div(
            className="field",
            children=field_children,
        )

        div.name = name

        return div
