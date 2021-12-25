import os
import urllib.parse
import logging
import pandas as pd
import yaml
from os.path import exists, isfile, join
from os import listdir

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_dangerously_set_inner_html

import helpsk as hlp

logging.basicConfig(
    format='[%(asctime)s %(levelname)-8s-%(funcName)30s()] %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# styling the sidebar
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '16rem',
    'padding': '2rem 1rem',
    'background-color': '#f8f9fa',
}

# padding for the page content
CONTENT_STYLE = {
    'margin-left': '18rem',
    'margin-right': '2rem',
    'padding': '2rem 1rem',
}

PROJECT_DIRECTORY = '../projects'
PROJECT_DIRECTORY_ = PROJECT_DIRECTORY + '/'
LABEL__MODEL_SUMMARY_LINK = "Summary"

project_names = [name for name in os.listdir(PROJECT_DIRECTORY) if os.path.isdir(PROJECT_DIRECTORY_ + name)]
project_names.sort()
project_dropdowns = [{'label': x, 'value': x} for x in project_names]

sidebar = html.Div(
    [
        html.H2("ML Explorer", className='display-6'),
        html.Hr(),
        html.P("Projects", className='lead'),
        dcc.Dropdown(
            id='project_names_dropdown',
            options=project_dropdowns,
            value=project_dropdowns[0]['value']
        ),
        html.Hr(),
        html.P("Models", className='lead'),
        dbc.Nav(
            id='model_links',
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id='page-content', children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    content
])


@app.callback(
    Output('model_links', 'children'),
    Output('url', 'pathname'),
    Input('project_names_dropdown', 'value')
)
def update_model_links(project_names_dropdown_value):
    """Updates the sidebar links to the models associated with the currently selected project. Also changes
    the URL to the first/default link "Summary of Models"
    """
    logging.debug(f"INPUT: project_names_dropdown_value: {project_names_dropdown_value}")

    if project_names_dropdown_value is None:
        logging.warning("Not expecting `project_names_dropdown_value is None`")
        raise PreventUpdate

    model_names = [name for name in os.listdir(PROJECT_DIRECTORY_ + project_names_dropdown_value)
                      if os.path.isdir(PROJECT_DIRECTORY_ + project_names_dropdown_value + '/' + name)]
    model_names.sort()
    model_names = [LABEL__MODEL_SUMMARY_LINK] + model_names
    model_links_children = [
        dbc.NavLink(x,
                    href=urllib.parse.quote('/' + project_names_dropdown_value + '/' + x),
                    external_link=False,
                    active='exact')
        for x in model_names
    ]

    new_address = urllib.parse.quote('/' + project_names_dropdown_value + '/' + LABEL__MODEL_SUMMARY_LINK)

    logging.debug(f"OUTPUT: model_names: {model_names}")
    logging.debug(f"OUTPUT: new_address: {new_address}")

    return model_links_children, new_address



def read_yaml(file_name) -> dict:
    with open(file_name, "r") as stream:
        yaml_dict = yaml.safe_load(stream)

    return yaml_dict

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page_content(path_name):
    logging.debug(f"INPUT: path_name: {path_name}")

    path_name = urllib.parse.unquote(path_name)
    paths = path_name.split('/')
    paths.remove('')
    current_project = paths[0]
    current_model = paths[1]
    current_content = [
        html.H2(f"{current_project} | {current_model}"),
        html.Hr()
    ]

    CURRENT_PROJECT_DIRECTORY = PROJECT_DIRECTORY_ + current_project
    CURRENT_MODEL_DIRECTORY = CURRENT_PROJECT_DIRECTORY + '/' + current_model
    logging.debug(f"CURRENT_MODEL_DIRECTORY: {CURRENT_MODEL_DIRECTORY}")

    #temp_file = CURRENT_PROJECT_DIRECTORY + "/Random Forest/Run 1 - Random Forest - BayesSearchCV.yaml"
    #parser = hlp.sklearn_eval.SearchCVParser.from_yaml_file(yaml_file_name = temp_file)
    #dash_dangerously_set_inner_html.DangerouslySetInnerHTML(parser.to_formatted_dataframe().render())


    metadata_file_name = CURRENT_PROJECT_DIRECTORY + '/project-metadata.yaml'

    if current_model == LABEL__MODEL_SUMMARY_LINK:

        metadata_dict = None
        if exists(metadata_file_name):

            metadata_dict = read_yaml(metadata_file_name)
            metadata_dict = metadata_dict['project']
            
            df = pd.DataFrame.from_dict(metadata_dict,orient='index')
            df = df.reset_index()
            df.columns=['name', 'values']

            about_content = [
                html.Br(),
                html.B(html.Div('project-metadata.yaml:')),
                dash_table.DataTable(
                            id='table',
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df.to_dict('records'),
                            style_header = {'display': 'none'},
                            style_cell={'textAlign': 'left'},
                )
            ]
        else:
            about_content = [
                html.Br(),
                html.H4("File Not Found: project-metadata.yaml", className="text-danger"),
            ]

        return current_content + [
            html.Div([
                dcc.Tabs([
                    dcc.Tab(label='Tab one', children=[
                        #dash_dangerously_set_inner_html.DangerouslySetInnerHTML(parser.to_formatted_dataframe().render())
                        
                        # dcc.Graph(
                        #     figure={
                        #         'data': [
                        #             {'x': [1, 2, 3], 'y': [4, 1, 2],
                        #                 'type': 'bar', 'name': 'SF'},
                        #             {'x': [1, 2, 3], 'y': [2, 4, 5],
                        #              'type': 'bar', 'name': u'Montréal'},
                        #         ]
                        #     }
                        # )
                    ]),
                    dcc.Tab(label='About', children=about_content),
                ])
            ])
        ]
    else:
        yaml_files = [f for f in listdir(CURRENT_MODEL_DIRECTORY)
                      if isfile(join(CURRENT_MODEL_DIRECTORY, f)) and f.endswith('.yaml')]

        logging.debug(f"yaml_files: {yaml_files}")
        
        return current_content + [
            html.P(yaml_files)
        ]



    # noinspection PyTypeChecker
    return current_content + [
            html.H3("404: Not found", className="text-danger"),
            html.P(f"The url path `{path_name}` was not found.")
        ]


if __name__ == '__main__':
    app.run_server(debug=True, port=3000)
