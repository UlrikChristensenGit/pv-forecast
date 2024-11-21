from dash import html


class Field:

    def __new__(
        cls,
        name: str,
        pickers: list[html.Div],
        helper_id: str = None,
    ) -> html.Div:
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

        div = html.Div(
            className="field",
            children=field_children,
        )

        div.name = name

        return div
