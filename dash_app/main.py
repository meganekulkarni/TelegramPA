import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os
from pandas import Series, DataFrame
from dash.dependencies import Input, Output
import dash_table as dtable
import plotly.graph_objects as go


app=dash.Dash()


# -------------------------- PYTHON FUNCTIONS ---------------------------- #


def add_numbers(first_num,second_num):
    new_num = first_num + second_num
    return new_num

def multiply_numbers(first_num,second_num):
    new_num = first_num * second_num
    return new_num


def build_banner():
    return html.Div(
        id='banner',
        className='banner',
        children=[
            html.Img(src=app.get_asset_url('dsc-logo2.png')),
        ],
    )

def TP_Sort():
    return html.Div([html.H1('Data Throughput Dashboard-NOC NPM Core'),
                dcc.Interval(id='graph-update',interval=10000),
                dtable.DataTable(id='my-table',
                                columns=[{"name": i, "id": i} for i in ["test","test2","test3","test4"]],
                                 data=[{}])])

def render_chart(df): 

    fig = go.Figure(go.Bar(
                x=[20, 14, 23],
                y=['giraffes', 'orangutans', 'monkeys'],
                orientation='h'))
        #     'data': [
        #         {'x': data_df.index.values.tolist(), 'y': data_df['add_num'], 'type': 'bar', 'name': 'Add Numbers'},
        #         {'x': data_df.index.values.tolist(), 'y': data_df['multiply_num'], 'type': 'bar', 'name': 'Multiply Numbers'},
        #     ],
        #     'layout': {
        #         'title': 'Dash Data Visualization'
        #     }
        # }
    dcc.Graph(
        id='my-graph',
        figure=fig
    )                

    # fig.show()

# -------------------------- LOAD DATA ---------------------------- #


csv_files_path = os.path.join('data/data.csv')

data_df = pd.read_csv(csv_files_path)

add_num_list = []
multiply_num_list = []

for index, row in data_df.iterrows():
    add_num_list.append(add_numbers(row['first_num'], row['second_num']))
    multiply_num_list.append(multiply_numbers(row['first_num'], row['second_num']))

data_df['add_num'] = add_num_list
data_df['multiply_num'] = multiply_num_list


# -------------------------- TEXT ---------------------------- #


dash_text = '''

This is an example of a DSC dashboard.
'''


# -------------------------- DASH ---------------------------- #


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, assets_folder='assets')
server = app.server

app.config.suppress_callback_exceptions = True


# -------------------------- PROJECT DASHBOARD ---------------------------- #


app.layout = html.Div(children=[
    html.H1(
        children=[
            build_banner(),
            html.P(
                id='instructions',
                children=dash_text),
            ]
    ),
    html.Div(
        children=[
            TP_Sort()
        ]
    ),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': data_df.index.values.tolist(), 'y': data_df['add_num'], 'type': 'bar', 'name': 'Add Numbers'},
                {'x': data_df.index.values.tolist(), 'y': data_df['multiply_num'], 'type': 'bar', 'name': 'Multiply Numbers'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])



# -------------------------- MAIN ---------------------------- #

@app.callback(Output('my-table', 'data'), [Input('graph-update', 'n_intervals')])
def update_table(n, maxrows=4):
    # We're now in interval *n*
    TP_Sort()
    TP_Table1='/home/keshev/Repos/TelegramPA/deploy-dash-with-gcp/simple-dash-app-engine-app/data/eggs.csv'
    TP_Table2=pd.read_csv(TP_Table1)
    return TP_Table2.to_dict(orient="records")

@app.callback(Output('my-graph', 'data'), [Input('graph-update', 'n_intervals')])
def update_graph(n, maxrows=4):
    # We're now in interval *n*
    TP_Sort()
    TP_Table1='/home/keshev/Repos/TelegramPA/deploy-dash-with-gcp/simple-dash-app-engine-app/data/eggs.csv'
    TP_Table2=pd.read_csv(TP_Table1)
    return TP_Table2.to_dict(orient="records")


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)