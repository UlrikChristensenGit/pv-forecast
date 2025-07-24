from dash import html

from . import form, results


def get_layout() -> html.Div:
    return html.Div(
        id="forecast",
        children=[
            form.get_form(),
            results.get_results(),
        ],
    )
