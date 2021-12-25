import os
import urllib.parse

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

PROJECT_DIRECTORY = '../projects'
PROJECT_DIRECTORY_ = PROJECT_DIRECTORY + '/'

project_names = [name for name in os.listdir(PROJECT_DIRECTORY) if os.path.isdir(PROJECT_DIRECTORY_ + name)]
project_names.sort()
project_dropdowns = [{'label': x, 'value': x} for x in project_names]

sidebar = html.Div(
    [
        html.H2("ML Explorer", className="display-6"),
        html.Hr(),
        html.P(
            "Projects", className="lead"
        ),
        dcc.Dropdown(
            id='project_names_dropdown',
            options=project_dropdowns,
            value=project_dropdowns[0]['value']
        ),
        html.Hr(),
        html.P(
            "Models", className="lead"
        ),
        dbc.Nav(
            id='model_links',
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])


@app.callback(
    Output('model_links', 'children'),
    Input('project_names_dropdown', 'value')
)
def update_model_links(project_names_dropdown_value):
    model_names = [name for name in os.listdir(PROJECT_DIRECTORY_ + project_names_dropdown_value)
                      if os.path.isdir(PROJECT_DIRECTORY_ + project_names_dropdown_value + '/' + name)]
    model_names.sort()
    model_names = ['Summary of Models'] + model_names
    model_links_children = [
        dbc.NavLink(x,
                    href=urllib.parse.quote('/' + project_names_dropdown_value + '/' + x),
                    active='exact')
        for x in model_names
    ]

    return model_links_children


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(path_name):
    path_name = urllib.parse.unquote(path_name)
    paths = path_name.split('/')
    paths.remove('')
    current_project = paths[0]
    current_model = paths[1]
    current_content = [
        html.H2(f"{current_project} | {current_model}"),
        html.Hr()
    ]

    # if path_name == "/":
    #     return [
    #             html.H1('asdf',
    #                     style={'textAlign':'center'}),
    #             dcc.Graph(id='asdf',
    #                      figure=px.bar(df, barmode='group', x='asdf',
    #                      y=['asdf', 'asdf']))
    #             ]
    # elif path_name == "/page-1":

    return current_content + [
            html.H3("404: Not found", className="text-danger"),
            html.P(f"The url path `{path_name}` was not found.")
        ]


if __name__ == '__main__':
    app.run_server(debug=True, port=3000)
