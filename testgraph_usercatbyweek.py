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
from datetime import datetime as dt
import pdb
from dotenv import load_dotenv
# dotenv to manage filepath to input files
load_dotenv()

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

app=dash.Dash()

# -------------------------- PYTHON FUNCTIONS ---------------------------- #

def build_banner():
    return html.Div(
        id='banner',
        className='banner',
        children=[
            html.Img(src=app.get_asset_url('plantmoney.jpg'),style={'height':'150px','width':'40%'}),
        ],
    )
    #
    ####   dropdown logic and date range selection was added here ####
    # spendcat selects based on spendcategory, user cat uses any col of input data (excl dates and system variables)
def dropdown_spendcat():
    category_options = [{'label':'All','value':'All'}]
    for spendcat in  tracker_df['category'].unique():
        category_options.append({'label':spendcat,'value':spendcat})
    return dcc.Dropdown(id='choosecat',
                        options = category_options,
                        value='All')
# user cat will show spend amounts by field of input data (excl dates and system variables) ..eg user name, title, etc
def dropdown_usercat():
    usercat_options = []
    ignorelist = ['id','input_datetime','message_date','datetime_logged','type','units','content','estimate','magnitude','user_id','datetm','weekid']
    for usercat in  tracker_df.columns:
        if usercat not in ignorelist:
            usercat_options.append({'label':usercat,'value':usercat})
    return dcc.Dropdown(id='chooseusercat',
                        options = usercat_options,
                        value='title')
def choose_daterange():
    return dcc.DatePickerRange(id='choosedates',
                        min_date_allowed=dt(2016,1,1),
                        max_date_allowed=dt.today(),
                        start_date=dt(2020,1,1),
                        end_date=dt.today())
### end of added sections
def render_chart():
    fig = dict({
        "data": [{}],
        "layout": {"title": {"text": "Spend By Category"}}
    })
    fig2 = go.Figure(fig)
    return dcc.Graph(id='my-graph',figure=fig2)

# -------------------------- DASH ---------------------------- #
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, assets_folder='assets')
server = app.server
app.config.suppress_callback_exceptions = True
#
### read spend data (formerly within render_chart but moved here as needed for dropdown)
spend_path = os.path.join(os.getenv("TELEGRAMPA_PROJECT_HOME"),"./dash_app/data/spend.csv")
if os.path.exists(spend_path):
#df = pd.read_csv(spend_path)
    tracker_json_list = update_tracker_data()
    tracker_df = pd.DataFrame(tracker_json_list)
    ## overrides to create testing data with different weekids and add category
    tracker_df['category']=tracker_df['status']

    tracker_df['datetm']=pd.to_datetime(tracker_df['input_datetime'], format="%Y-%m-%d %H:%M:%S.%f")
    tracker_df['weekid']=tracker_df['datetm'].apply(lambda x:x.isocalendar()[1])
    ### apply data overrides for testing
    tracker_df.at[1, 'category']="Special"
    tracker_df.at[2, 'category']="Special"
    tracker_df.at[2, 'weekid']=29
else:
    print('error, no input spending data')



# -------------------------- PROJECT DASHBOARD ---------------------------- #


app.layout = html.Div(children=[
    html.H1(children=[build_banner(),
                html.P(id='instructions',
                children='Personal Dashboard!',style={'fontSize':36, 'color' : 'blue' })
            ]
    ),
       # add in dropdown for graph
       # then draw graph
    html.Div([html.H3("Select spending category to track: ",style={'fontSize':24}),
            html.Div(children=[dropdown_spendcat()],style={'width':'40%', 'display':'inline-block'}),
            ]),
    html.Div([html.H3("Show spend amount for each: ",style={'fontSize':24}),
            html.Div(children=[dropdown_usercat()],style={'width':'40%', 'display':'inline-block'}),
            ]),
    html.Div([html.H3("Select start and end date: ",style={'fontSize':24}),
            html.Div(children=[choose_daterange()],style={'width':'40%','display':'inline-block'})
            ]),
    html.Div(children=[render_chart()],style={'width' : '65%'})
])

# -------------------------- MAIN ---------------------------- #

@app.callback(Output('my-graph', 'figure'),
    [Input('choosecat', 'value'),
     Input('chooseusercat', 'value'),
     Input('choosedates','start_date'),
     Input('choosedates','end_date')
     ])
def update_graph(selected_cat,usergraph_cat,startdt_graph,enddt_graph):
    ###TODO selected tracker status needs to be an input of some sort and updatable by the user
    # We're now in interval *n*
    render_chart()
    startdt=dt.strptime(startdt_graph[:10],'%Y-%m-%d')
    enddt=dt.strptime(enddt_graph[:10],'%Y-%m-%d')
    if selected_cat == 'All':
        tracker_df_cat = tracker_df
    else:
        tracker_df_cat = tracker_df[tracker_df["category"]==selected_cat]
    #
    tracker_df_cat = tracker_df_cat[(tracker_df_cat["datetm"] >= startdt) &
                                    (tracker_df_cat["datetm"] <= enddt)]
    ##     within each bar, show different color for each calendar week
    weekblocks=[]
    rgb_red=0
    for spendweek in sorted(tracker_df_cat['weekid'].unique()):
        tracker_df_cat_week = tracker_df_cat[tracker_df_cat['weekid']==spendweek]
        #grouped_df = tracker_df_cat_week.groupby(usergraph_cat, as_index=False).agg({"magnitude":"sum"}).sort_values("magnitude",ascending=True)
        grouped_df = tracker_df_cat_week.groupby(usergraph_cat, as_index=False).agg({"magnitude":"sum"})
        rgb_red += 50
        rgbstr='rgb('+str(rgb_red)+',0,248)'
        weekblocks.append(
        {"type": "bar",
            "x": grouped_df['magnitude'],
            "y": grouped_df[usergraph_cat],
            "text": grouped_df['magnitude'],
            "texttemplate" : "%{text:.0f}",
            "textposition": "auto",
            "name": "Calendar week "+str(spendweek),
            "opacity": .5,
            "marker":{"color": rgbstr},
            "orientation":'h'})

    fig = dict({
            "data": weekblocks,
            "layout": {"title": {"text": "Spending for Category:  "+selected_cat},
                       "barmode" : "stack",
                       "xaxis_title": "$ spent in period",
                       "xaxis_tickprefix" : "$", "xaxis_tickformat" : ",.",
                       "yaxis" : {"categoryorder":"total ascending"}
                       }
        })

    fig2 = go.Figure(fig)
    return fig2


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
