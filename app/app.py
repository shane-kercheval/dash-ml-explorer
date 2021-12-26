import os
import urllib.parse
import logging
import pandas as pd
import numpy as np
import os

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate
import dash_dangerously_set_inner_html

import plotly.express as px

import helpsk as hlp

from helper_functions import *


PROJECTS_DIRECTORY = '../projects'
LABEL__MODEL_SUMMARY_LINK = "Summary"

logging.basicConfig(
    format='[%(asctime)s %(levelname)-8s-%(funcName)30s()] %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

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

project_names = [name for name in os.listdir(PROJECTS_DIRECTORY)
                 if os.path.isdir(os.path.join(PROJECTS_DIRECTORY, name))]
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

    project_directory = os.path.join(PROJECTS_DIRECTORY, project_names_dropdown_value)
    model_names = [name for name in os.listdir(project_directory)
                   if os.path.isdir(os.path.join(project_directory, name))]
    model_names.sort()
    model_names = [LABEL__MODEL_SUMMARY_LINK] + model_names
    model_links_children = [
        dbc.NavLink(x,
                    href=urllib.parse.quote(os.path.join('/', project_names_dropdown_value, x)),
                    external_link=False,
                    active='exact')
        for x in model_names
    ]

    new_address = urllib.parse.quote(os.path.join('/',
                                                  project_names_dropdown_value,
                                                  LABEL__MODEL_SUMMARY_LINK))

    logging.debug(f"OUTPUT: model_names: {model_names}")
    logging.debug(f"OUTPUT: new_address: {new_address}")

    return model_links_children, new_address


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

    CURRENT_PROJECT_DIRECTORY = os.path.join(PROJECTS_DIRECTORY, current_project)
    CURRENT_MODEL_DIRECTORY = CURRENT_PROJECT_DIRECTORY + '/' + current_model
    logging.debug(f"CURRENT_MODEL_DIRECTORY: {CURRENT_MODEL_DIRECTORY}")

    #temp_file = CURRENT_PROJECT_DIRECTORY + "/Random Forest/Run 1 - Random Forest - BayesSearchCV.yaml"
    #parser = hlp.sklearn_eval.SearchCVParser.from_yaml_file(yaml_file_name = temp_file)
    #dash_dangerously_set_inner_html.DangerouslySetInnerHTML(parser.to_formatted_dataframe().render())

    metadata_file_name = CURRENT_PROJECT_DIRECTORY + '/project-metadata.yaml'

    if current_model == LABEL__MODEL_SUMMARY_LINK:

        metadata_dict = None
        if os.path.exists(metadata_file_name):

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

        # noinspection PyTypeChecker
        return current_content + [
            html.Div([
                dcc.Tabs([
                    
                    dcc.Tab(label='About', children=about_content),
                    dcc.Tab(label='Tab one', children=[
                        # dash_dangerously_set_inner_html.DangerouslySetInnerHTML(parser.to_formatted_dataframe().render())
                        
                        dcc.Graph(
                            figure={
                                'data': [
                                    {'x': [1, 2, 3], 'y': [4, 1, 2],
                                        'type': 'bar', 'name': 'SF'},
                                    {'x': [1, 2, 3], 'y': [2, 4, 5],
                                     'type': 'bar', 'name': u'Montréal'},
                                ]
                            }
                        )
                    ]),
                ])
            ])
        ]
    else:
        yaml_files = [f for f in os.listdir(CURRENT_MODEL_DIRECTORY)
                      if os.path.isfile(os.path.join(CURRENT_MODEL_DIRECTORY, f)) and f.endswith('.yaml')]
        #yaml_files = yaml_files + ['Run 1.yaml']*10
        yaml_files.sort(reverse=True)

        logging.debug(f"yaml_files: {yaml_files}")

        tabs = []
        # noinspection PyTypeChecker
        for yaml_file in yaml_files:
            name = yaml_file.split('.')[0]

            # if name == 'Final Model':
            #     children = []
            # else:
            #     parser = hlp.sklearn_eval.SearchCVParser.from_yaml_file(yaml_file_name = os.path.join(CURRENT_PROJECT_DIRECTORY, current_model, yaml_file))
            #     score_df = parser.to_dataframe(sort_by_score=False)
            #     score_df['labels'] = [x.replace('{', '<br>').replace(', ', '<br>').replace('}', '')
            #                   for x in parser.iteration_labels(order_from_best_to_worst=False)]

            #     fig = px.scatter(
            #         data_frame=score_df,
            #         x=np.arange(0, parser.number_of_iterations),
            #         y=parser.primary_score_name + " Mean",
            #         title='Average Cross-Validation Score across all iterations',
            #         trendline='lowess',
            #         labels={'x': 'Iteration'},
            #         custom_data=['labels'],
            #         height=600,
            #         width=600*hlp.plot.GOLDEN_RATIO
            #     )
            #     fig.update_traces(
            #         hovertemplate="<br>".join([
            #             "Iteration: %{x}",
            #             "roc_auc Mean: %{y}",
            #             "<br>Parameters: %{customdata[0]}",
            #         ])
            #     )

            #     #scatter_trend_line = 'ols'
            #     scatter_trend_line = 'lowess'
            #     #feature_color = 'encoder'
            #     feature_color = 'scaler'
            #     fig2 = px.scatter(
            #         data_frame=score_df,
            #         x='max_features',
            #         y=parser.primary_score_name + " Mean",
            #         size='n_estimators',
            #         color=feature_color,
            #         title='max_features',
            #         trendline=scatter_trend_line,
            #         #labels={'x': 'Iteration'},
            #         custom_data=['labels'],
            #         height=600,
            #         width=600*hlp.plot.GOLDEN_RATIO
            #     )

            #     fig2.update_traces(
            #         hovertemplate="<br>".join([
            #             "Iteration: %{x}",
            #             "roc_auc Mean: %{y}",
            #             "<br>Parameters: %{customdata[0]}",
            #         ])
            #     )

            #     children = [
            #         dcc.Graph(id='asdf', figure=fig),
            #         dcc.Graph(id='asdf2', figure=fig2),
            #         dash_dangerously_set_inner_html.DangerouslySetInnerHTML(parser.to_formatted_dataframe().render())

            #     ]
            tabs = tabs + [
                dcc.Tab(
                    id={
                        'type': 'my-tab',
                        'index': name
                    },
                    value=name,
                    label=name
                )
            ]
                
        return current_content + [
            dcc.Loading(children=html.Div([
                dcc.Tabs(
                    id='model_tabs',
                    children=tabs,
                    value=yaml_files[0].split('.')[0])
            ]))
        ]

    # noinspection PyTypeChecker
    return current_content + [
            html.H3("404: Not found", className="text-danger"),
            html.P(f"The url path `{path_name}` was not found.")
        ]


@app.callback(
    Output({'type': 'my-tab', 'index': MATCH}, 'children'),
    Input('model_tabs', 'value'),
    State('url', 'pathname'),
)
def display_output(value, path_name):

    # if value is None or value == 'tab-1':
    #     raise PreventUpdate

    print(value)
    print(path_name)
    path_name = urllib.parse.unquote(path_name)
    paths = path_name.split('/')
    paths.remove('')
    current_project = paths[0]
    current_model = paths[1]
    current_content = [
        html.H2(f"{current_project} | {current_model}"),
        html.Hr()
    ]

    CURRENT_PROJECT_DIRECTORY = os.path.join(PROJECTS_DIRECTORY, current_project)
    CURRENT_MODEL_DIRECTORY = CURRENT_PROJECT_DIRECTORY + '/' + current_model
    logging.debug(f"CURRENT_MODEL_DIRECTORY: {CURRENT_MODEL_DIRECTORY}")


    if value == 'Final Model':
        children = []
    else:
        parser = hlp.sklearn_eval.SearchCVParser.from_yaml_file(yaml_file_name = os.path.join(CURRENT_PROJECT_DIRECTORY, current_model, value + '.yaml'))
        #parser = hlp.sklearn_eval.SearchCVParser.from_yaml_file(yaml_file_name = os.path.join(CURRENT_PROJECT_DIRECTORY, current_model, 'Run 1' + '.yaml'))
        score_df = parser.to_dataframe(sort_by_score=False)
        score_df['labels'] = [x.replace('{', '<br>').replace(', ', '<br>').replace('}', '')
                      for x in parser.iteration_labels(order_from_best_to_worst=False)]

        fig = px.scatter(
            data_frame=score_df,
            x=np.arange(0, parser.number_of_iterations),
            y=parser.primary_score_name + " Mean",
            #title='Bayesian Performance Over Time',
            trendline='lowess',
            labels={'x': 'Iteration'},
            custom_data=['labels'],
            height=600,
            #width=600*hlp.plot.GOLDEN_RATIO
        )
        fig.update_traces(
            hovertemplate="<br>".join([
                "Iteration: %{x}",
                "roc_auc Mean: %{y}",
                "<br>Parameters: %{customdata[0]}",
            ])
        )

        children = [
            html.Br(),html.Br(),
            dbc.Row([
                html.H3("Overview"),
                html.Br(),html.Br(),
                dbc.Col(
                    children=[
                        html.H6("Bayesian Performance Over Time"),
                        dcc.Graph(id='bayesian_performance', figure=fig),
                    ],
                    width=5
                ),
                dbc.Col(
                    children=[
                        html.H6("Best Performance Parameters"),
                        dash_dangerously_set_inner_html.DangerouslySetInnerHTML(parser.to_formatted_dataframe().render())
                    ],
                    width=7
                )
            ]),
            dbc.Row(
                children=[
                    html.H3("Cross-Validation Performance"),
                    dbc.Col(
                        children=[
                            html.Br(),html.Br(),
                            dbc.Row([
                                html.Label(
                                    "X-Axis",
                                    style={'font-weight': 'bold'}
                                ),
                                dcc.Dropdown(
                                    id='model_graph_custom_variable_x',
                                    options=[{'label':x, 'value':x} for x in parser.parameter_names],
                                    value=parser.parameter_names[0]
                                ),
                            ], style={'margin-top': '50px'}),
                            dbc.Row([
                                html.Label(
                                    "Color",
                                    style={'font-weight': 'bold'}
                                ),
                                dcc.Dropdown(
                                    id='model_graph_custom_variable_color',
                                    options=[{'label':x, 'value':x} for x in parser.parameter_names],
                                    value=None
                                ),
                            ]),
                            dbc.Row([
                                html.Label(
                                    "Size",
                                    style={'font-weight': 'bold'}
                                ),
                                dcc.Dropdown(
                                    id='model_graph_custom_variable_size',
                                    options=[{'label':x, 'value':x} for x in parser.parameter_names],
                                    value=None
                                ),
                            ]),
                            dbc.Row([
                                html.Label(
                                    "Trendline",
                                    style={'font-weight': 'bold'}
                                ),
                                dcc.RadioItems(
                                    id='model_graph_custom_variable_trendline',
                                    options=[
                                        {'label': 'None', 'value': 'None'},
                                        {'label': 'Regression Line', 'value': 'ols'},
                                        {'label': 'Lowess', 'value': 'lowess'},
                                    ],
                                    value='lowess',
                                    labelStyle={'display': 'flex'}
                                ),
                            ])
                        ],
                        width=2
                    ),
                    dbc.Col(
                        children=[
                            dcc.Loading(dcc.Graph(id='model_graph_custom')),
                        ],
                        width=10
                    ),
                ]
            )
        ]


    return html.Div(children)



@app.callback(
    Output('model_graph_custom', 'figure'),
    Input('model_graph_custom_variable_x', 'value'),
    Input('model_graph_custom_variable_color', 'value'),
    Input('model_graph_custom_variable_size', 'value'),
    Input('model_graph_custom_variable_trendline', 'value'),
    
    State('url', 'pathname'),
    State('model_tabs', 'value'),
)
def update_model_graph_custom(x_variable, color_variable, size_variable, trend_line, path_name, model_tabs_value):
    path_name = urllib.parse.unquote(path_name)
    paths = path_name.split('/')
    paths.remove('')
    current_project = paths[0]
    current_model = paths[1]

    CURRENT_PROJECT_DIRECTORY = os.path.join(PROJECTS_DIRECTORY, current_project)
    CURRENT_MODEL_DIRECTORY = CURRENT_PROJECT_DIRECTORY + '/' + current_model


    parser = hlp.sklearn_eval.SearchCVParser.from_yaml_file(yaml_file_name = os.path.join(CURRENT_PROJECT_DIRECTORY, current_model, model_tabs_value + '.yaml'))
    score_df = parser.to_dataframe(sort_by_score=False)
    score_df['labels'] = [x.replace('{', '<br>').replace(', ', '<br>').replace('}', '')
                  for x in parser.iteration_labels(order_from_best_to_worst=False)]

    ##scatter_trend_line = 'ols'
    #scatter_trend_line = 'lowess'
    if trend_line == 'None':
        trend_line = None
    fig2 = px.scatter(
        data_frame=score_df,
        x=x_variable,
        y=parser.primary_score_name + " Mean",
        size=size_variable,
        color=color_variable,
        #title=f'Cross Validation Performance ({parser.primary_score_name})',
        trendline=trend_line,
        #labels={'x': 'Iteration'},
        custom_data=['labels'],
        height=600,
        #width=600*hlp.plot.GOLDEN_RATIO
    )

    fig2.update_traces(
        hovertemplate="<br>".join([
            "Iteration: %{x}",
            "roc_auc Mean: %{y}",
            "<br>Parameters: %{customdata[0]}",
        ])
    )

    return fig2





if __name__ == '__main__':
    app.run_server(debug=True, port=3000)

# from dash import Dash
# import time
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output


# app = Dash(__name__)
# app.layout = html.Div(
#     children=[
#         html.H3("Edit text input to see loading state"),
#         dcc.Input(id="loading-input-1", value="Input triggers local spinner"),
#         dcc.Loading(
#             id="loading-1", type="default", children=html.Div(id="loading-output-1")
#         ),
#     ],
# )


# @app.callback(
#     Output("loading-output-1", "children"),
#     Input("loading-input-1", "value"),
#     prevent_initial_call=True,
# )
# def input_triggers_spinner(value):
#     time.sleep(2)
#     return value


# if __name__ == "__main__":
#     app.run_server(debug=True, port=3000)