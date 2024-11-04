from dash import html


class Field:

    def __init__(
        self,
        name: str,
        pickers: list[html.Div],
        helper_id: str = None,
    ):
        self.name = name
        field_body_children = [
            html.Div(
                className="field-pickers",
                children=pickers,
            ),
        ]

        if helper_id:
            field_body_children.append(
                html.Div(
                    className="field-helper",
                    id=helper_id,
                )
            )

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

        self.container = html.Div(
            className="field",
            children=field_children,
        )
