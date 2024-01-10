from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import dash
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import json
import dash_bootstrap_components as dbc
import numpy as np
from dotenv import load_dotenv
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

race_df = pd.read_csv("dashboard_data/race_df.csv")

edu_df = pd.read_csv("dashboard_data/edu_df.csv")

counties = pd.read_csv("dashboard_data/counties_new.csv")


#map
load_dotenv()
API_KEY = os.environ.get("API_KEY", "default_val")
px.set_mapbox_access_token(API_KEY)

fig = px.scatter_mapbox(counties, lat="lat", lon="long", 
                         hover_name="county", zoom=6, 
                         center={'lat':37.7749, 'lon':-122.4194}, size='population', size_max=50)
fig.update_layout(
    height=800,
    width=500)
fig.update_layout(clickmode='event+select')
fig.update_mapboxes(bounds={'east':-114.8, 'north':42.0095, 
                             'south':32.5343, 'west':-124.24})

fig.update_traces(customdata=counties['county'])

app.layout = html.Div(children=[html.Div(children=[
    html.H2(f"California County Snapshot: Exploring the Numbers",
            className="display-5 text-center"),
    html.P(["Welcome to the California County Snapshot! ",
            "I am ", 
            html.A("Ayumu Justin Ueda", href="https://www.linkedin.com/in/ayumu-ueda-ab1879224/", target="_blank"),
            ", a data science major at UC Berkeley. ", 
            "This dashboard allows you to explore data from each county in California gathered from ",
            html.A("census.org.", href="https://data.census.gov/", target="_blank"),
            " ",
            "Dive into each county's info by hovering over the map—the plot changes with your mouse's position!"],
            className="small text-center", style={'width': '80%', 'margin': 'auto'})
            ]),
    
    html.Div(className="lower than title", children=[

    html.Div(
    className="col-md-6",
    children=[

    dcc.Graph(
        id='basic-interactions_map',
        figure=fig,
        hoverData={'points':[{'customdata' : 'Alameda'}]}
    )],
    style={'padding': 0, 'flex': 1, 'flexDirection':"column", 'margin':0}
    ),

    html.Div(
    className="col-md-6",
    children=[

      html.Div(children=[
        dcc.Graph(
        id='Indicator'
    )]),

     html.Div(children=[
         dcc.Graph(
        id='Piechart',
    )])],
    style={'padding': 0, 'flex': 1, 'flexDirection':"row", 'margin':0}
    ),

    html.Div(
    className="col-md-6",
    children=[

      html.Div(children=[dcc.Graph(
        id='line_chart'
    )]),

      html.Div(children=[dcc.Graph(
        id='h_bar'
    )])],
    style={'padding': 0, 'flex': 1, 'flexDirection':"row", 'margin':0}
    )
],
style={'display': 'flex', 'flexDirection': 'row', 'padding': 0, 'margin':0}
)], style={'display': 'flex', 'flexDirection': 'column', 'padding': 0, 'margin':0}
)


@callback(
    Output('Indicator', 'figure'),
    Input('basic-interactions_map', 'hoverData'))
def update_hover_data(hoverData):
    
    dff = counties[counties['county'] == hoverData['points'][0]['customdata']]

    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = dff['median_age'].values[0],
        domain = {'row': 0, 'column': 0, 'x': [0, 0.3]},
        delta = {'reference': np.mean(counties['median_age']), 'relative': True, 'valueformat':".0%"},
        title = {'text': "Median Age"},
        number = {'suffix': "yo"}
        ))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = dff['poverty_rate'].values[0],
        delta = {'reference': np.mean(counties['poverty_rate']), 'relative': True, 'valueformat':".0%"},
        domain = {'row': 1, 'column': 0, 'x': [0, 0.3]},
        title = {'text': "Poverty Rate"},
        number = {'suffix': "%"} 
        ))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = dff['population'].values[0],
        delta = {'reference': np.mean(counties['population']), 'relative': True, 'valueformat':".0%"},
        domain = {'row': 1, 'column': 1, 'x': [0.7, 1]},
        title = {'text': "Population"}
        ))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = dff['median_income'].values[0],
        number = {'prefix': "$"},
        delta = {'reference': np.mean(counties['median_income']), 'relative': True, 'valueformat':".0%"},
        domain = {'row': 0, 'column': 1, 'x': [0.7, 1]},
        title = {'text': "Median Income"}
        ))

    fig.update_layout(
        grid = {'rows': 2, 'columns': 2, 'pattern': "independent"})
    fig.update_layout(
    grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
    height=400,  # Set your desired height
    width=450   # Set your desired width
)
    return fig


@callback(
    Output('Piechart', 'figure'),
    Input('basic-interactions_map', 'hoverData'))
def update_pie_data(hoverData):
    race_dff = race_df[race_df['county'] == hoverData['points'][0]['customdata']].drop(['county'], axis=1)
    race_dff = race_dff.T.reset_index()
    race_dff.columns = ['race', 'number']
    fig = px.pie(race_dff, values='number', 
                 names='race', hole=.3)
    fig.update_layout(
    
    legend=dict(
        orientation="h",  # horizontal orientation
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),

    title=dict(
        text='Racial Composition',
        y=1.0,  # Adjust the y-position to place the title below the chart
        x=0.5   # Center the title along the x-axis
    ),

    font=dict(size=10)
    )
    
    # fig.update_layout(showlegend=False)
    fig.update_layout(
    height=400,  # Set your desired height
    width=450   # Set your desired width
)
    return fig

@callback(
    Output('line_chart', 'figure'),
    Input('basic-interactions_map', 'hoverData'))
def update_line_data(hoverData):

    year_list = ['2017', '2018', '2019', '2021', '2022']
    county_name = hoverData['points'][0]['customdata']
    counties_sp = counties[counties['county'] == county_name]
    average_price = counties[year_list].mean(axis=0)

    counties_sp = counties_sp[year_list].T.reset_index()
    counties_sp.columns = ['Year', 'Price']
    average_price = pd.DataFrame(average_price).reset_index()
    average_price.columns = ['Year', 'Price']
    counties_sp['Group'] = county_name
    average_price['Group'] = "Average"
    counties_sp = pd.concat([counties_sp, average_price], axis=0)
    fig = px.line(counties_sp, x='Year', 
                  y='Price', color='Group', 
                  markers=True)
    fig.update_layout(
    height=400,
    width=550,
    title=dict(
        text="Median Housing Price Overview",
        x = 0.5
    ))
    fig.update_yaxes(range=[200000.0, 1700000.0])
    return fig

@callback(
    Output('h_bar', 'figure'),
    Input('basic-interactions_map', 'hoverData'))
def update_h_bar_data(hoverData):
    edu_df = pd.read_csv("dashboard_data/edu_df.csv")
    eduu_df = edu_df.copy()
    county_name = hoverData['points'][0]['customdata']
    edu_df = edu_df[edu_df['county'] == county_name]
    edu_df = edu_df.drop(['county'], axis=1)
    edu_df = edu_df.reset_index(drop=True)
    edu_df = edu_df.T.reset_index()
    edu_df.columns = ['Major', 'Ratio(%)']
    edu_df['Group'] = county_name
    eduu_df = eduu_df.drop('county', axis=1).mean().reset_index()
    eduu_df.columns = ['Major', 'Ratio(%)']
    eduu_df['Group'] = 'Average'
    edu_df = pd.concat([edu_df, eduu_df])
    fig = px.bar(edu_df,
            x="Ratio(%)",
            y="Major",
            orientation='h',
            color="Group", 
             barmode="group")
    
    fig.update_layout(
    height=400,
    width=550,
    title=dict(
        text="Bachelor's Degrees by Field (Age 25+) Ratio",
        x = 0.5,

    )
    )
    fig.update_xaxes(range=[0.0, 60.0])

    return fig


if __name__ == '__main__':
    app.run(debug=True)