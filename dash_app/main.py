import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os
import json
from pandas import Series, DataFrame
from dash.dependencies import Input, Output
import dash_table as dtable
import plotly.graph_objects as go
import react_dnd as react_dnd
from dotenv import load_dotenv

load_dotenv()

todo_data = [
  {
    "id": 1,
    "status": "open",
    "title": "Human Interest Form",
    "content": "Fill out human interest distribution form",
    "estimate": "30m"
  },
  {
    "id": 2,
    "status": "open",
    "title": "Purchase present",
    "content": "Get an anniversary gift",
    "estimate": "4h"
  },
  {
    "id": 3,
    "status": "open",
    "title": "Invest in investments",
    "content": "Call the bank to talk about investments",
    "estimate": "1d"
  },
  {
    "id": 4,
    "status": "open",
    "title": "Daily reading",
    "content": "Finish reading Intro to UI/UX",
    "estimate": "2w"
  }
]

def update_tracker_data(): 
    tracker_path = os.path.join(os.getenv("TELEGRAMPA_PROJECT_HOME"),"dash_app/data/tracker_data/")
    tracker_jsons = os.listdir(tracker_path)

    json_list = []
    for tracker_json in tracker_jsons: 
        filepath = os.path.join(tracker_path, tracker_json)
        with open(filepath, "r") as fp:
            json_data = json.load(fp)
            json_data.pop("attributes")
            json_list.append(json_data)
    
    return json_list


tracker_json_list = update_tracker_data()
todo_statuses = ['open', 'in progress', 'in review', 'done']

###with Rob's stuff I can provide a list of the column headers, then provide data. This gets binned into the appropriate list based on the status field
#TODO NEXT
#Use Cases for list module
#From telegram:
    #add to an existing list
    #create a new list

#key-value store
# One datastore with the titles, potentially some metadata
#{
#   "groceries": { "created_at":2020-07-18,
#                  ""
#
#           }
#
#
#}

#One datastore for current data
#One datastore for the historical data

#TODO NEXT
#Create schemas for these datastores


app=dash.Dash()


# -------------------------- PYTHON FUNCTIONS ---------------------------- #


def build_banner():
    return html.Div(
        id='banner',
        className='banner',
        children=[
            html.Img(src=app.get_asset_url('touching-tips.jpg'), height="50px",width="100px"),
        ],
    )

def TP_Sort():
    return html.Div([html.H1('Data Throughput Dashboard-NOC NPM Core'),
                dcc.Interval(id='graph-update',interval=10000),
                dtable.DataTable(id='my-table',
                                columns=[{"name": i, "id": i} for i in ["date","unix_timestamp","category","full_text"]],
                                 data=[{}])])

def render_chart(): 

    fig = dict({
        "data": [{}],
        "layout": {"title": {"text": "Spend By Category"}}
    })

    fig2 = go.Figure(fig)
        #     'data': [
        #         {'x': data_df.index.values.tolist(), 'y': data_df['add_num'], 'type': 'bar', 'name': 'Add Numbers'},
        #         {'x': data_df.index.values.tolist(), 'y': data_df['multiply_num'], 'type': 'bar', 'name': 'Multiply Numbers'},
        #     ],
        #     'layout': {
        #         'title': 'Dash Data Visualization'
        #     }
        # }
    return dcc.Graph(
        id='my-graph',
        figure=fig2
    )                

def render_tracker_lists(): 
    json_list = update_tracker_data()
    statuses = list(set([x["status"] for x in json_list]))

    return react_dnd.ReactDnd(
            id="react-dnd",
            data=json_list,
            statuses=statuses
        )
    # fig.show()

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

#TODO NEXT get rid of the duplicated list

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

    html.Div(id="tracker-list-controller",
      children=(render_tracker_lists(),
      )
    ),

    html.Div(
      id="todo-output"
    ),

    html.Div(
        children=[
            render_chart()
        ]
    )
])



# -------------------------- MAIN ---------------------------- #

@app.callback(Output('my-table', 'data'), [Input('graph-update', 'n_intervals')])
def update_table(n, maxrows=4):
    # We're now in interval *n*

    #right now it's just polling a file. I'll see if the input structure can actually accept changes to a file saved on disk
    TP_Sort()
    #logpath ='./data/full_log.csv'
    logpath = os.path.join(os.getenv("TELEGRAMPA_PROJECT_HOME"),"./dash_app/data/full_log.csv")
    if os.path.exists(logpath):
        TP_Table2=pd.read_csv(logpath)
        return TP_Table2.to_dict(orient="records")
    else:
        return [{}]

@app.callback(Output('my-graph', 'figure'), [Input('graph-update', 'n_intervals')])
def update_graph(n, maxrows=4):
    # We're now in interval *n*

    render_chart()
    spend_path = os.path.join(os.getenv("TELEGRAMPA_PROJECT_HOME"),"./dash_app/data/spend.csv")
    if os.path.exists(spend_path):
        #df = pd.read_csv(spend_path)
        tracker_json_list = update_tracker_data() 
        tracker_df = pd.DataFrame(tracker_json_list)

        ###TODO selected tracker status needs to be an input of some sort and updatable by the user
        selected_tracker_status = "Spend"
        tracker_df = tracker_df[tracker_df["status"]==selected_tracker_status]
        grouped_df = tracker_df.groupby("title", as_index=False).agg({"magnitude":"sum"}).sort_values("magnitude",ascending=True)
        fig = dict({
            "data": [{"type": "bar",
                "x": grouped_df['magnitude'],
                "y": grouped_df['title'],
                "orientation":'h'}],
            "layout": {"title": {"text": "Spend By Category"}}
        })

        fig2 = go.Figure(fig)
        return fig2
    else:
        fig = dict({
            "data": [{}],
            "layout": {"title": {"text": "Spend By Category"}}
        })

        fig2 = go.Figure(fig)
            #     'data': [
            #         {'x': data_df.index.values.tolist(), 'y': data_df['add_num'], 'type': 'bar', 'name': 'Add Numbers'},
            #         {'x': data_df.index.values.tolist(), 'y': data_df['multiply_num'], 'type': 'bar', 'name': 'Multiply Numbers'},
            #     ],
            #     'layout': {
            #         'title': 'Dash Data Visualization'
            #     }
            # }
        return dcc.Graph(
            id='my-graph',
            figure=fig2
        )              



@app.callback(
    Output(component_id='react-dnd', component_property='data'),
    [Input('graph-update', 'n_intervals')]
)
def update_tracker_list_controller_data(n, maxrows=4):
    return update_tracker_data()

@app.callback(
    Output(component_id='todo-output', component_property='children'),
    [Input(component_id='react-dnd', component_property='data')]
)

def display_output(value):
    return json.dumps(value)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)