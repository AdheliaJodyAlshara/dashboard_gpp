import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
from statistics import mode
import plotly.express as px

print('BERHASIL')

app = dash.Dash(
    external_stylesheets=[dbc.themes.MINTY],
    name = 'Global Power Plant'
)

app.title = 'Power Plant Dashboard Analytics'

## ---Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
    ],
    brand="Global Power Plant Dashboard Analytics",
    brand_href="#",
    color="primary",
    dark=True,
)

## ---Import dataset
gpp=pd.read_csv('power_plant.csv')

## -- Card content
total_country = [
    dbc.CardHeader('Number of Country'),
    dbc.CardBody([
        html.H1(gpp['country_long'].nunique())
    ]),
]

total_pp = [
    dbc.CardHeader('Total Power Plant'),
    dbc.CardBody([
        html.H1(gpp['name of powerplant'].nunique())
    ]),
]

total_fuel = [
    dbc.CardHeader('Most Used Fuel',),
    dbc.CardBody([
        html.H1(f"{mode(gpp['primary_fuel'])} = {len(gpp[gpp['primary_fuel']==(gpp.describe(include='object')).loc['top','primary_fuel']])}")
    ])
]


## --Visualization
# Data aggregation
agg1 = pd.crosstab(
    index=[gpp['country code'], gpp['start_year']],
    columns='No of Power Plant'
).reset_index()

# Visualization
plot_map = px.choropleth(agg1,
             locations='country code',
              color_continuous_scale='tealgrn',
             color='No of Power Plant',
             animation_frame='start_year',
             template='ggplot2')


## --LAYOUT
app.layout = html.Div(children=[
    navbar,
    html.Br(),
    
    ## --Component Main Page--

    html.Div([

        ## --Row1
        dbc.Row([
            ### Column 1
            dbc.Col([
                dbc.Card(total_country, color='LightCyan'),
                html.Br(),
                dbc.Card(total_pp, color='PaleTurquoise'),
                html.Br(),
                dbc.Card(total_fuel, color='PowderBlue'),
                html.Br(),
            ],
            width=3),

            ### Column 2
            dbc.Col([
                dcc.Graph(figure=plot_map),
            ], width=9),
        ]),

        html.Hr(),

        ## --Row2
        dbc.Row([
            ### Column 1
            dbc.Col([
                html.H1('Analysis by Country'),
                dbc.Tabs([
                    ## ---TAB 1: ranking
                    dbc.Tab(
                        dcc.Graph(
                            id='plotranking',
                        ),
                        label='Ranking'),

                    ## --TAB 2 : distribution
                    dbc.Tab(
                        dcc.Graph(
                            id='plotdistribut',
                        ), label='Distribution'),
                ]),
            ], width=8),

            ### Column 2
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Select Country'),
                    dbc.CardBody(
                        dcc.Dropdown(
                            id='choose_country',
                            options=gpp['country_long'].unique(),
                            value='Indonesia',
                        ),
                    ),
                ]),
                dcc.Graph(
                    id='plotpie',
                ),
            ],
            width=4),
        ]),
    ], style={
        'paddingLeft':'30px',
        'paddingRight':'30px',
    })
])

## Callback Plot Ranking
@app.callback(
    Output(component_id='plotranking', component_property='figure'),
    Input(component_id='choose_country', component_property='value'),
)

def update_plot1(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]

    top_indo = gpp_indo.sort_values('capacity in MW').tail(10)


    plot_ranking = px.bar(
        top_indo,
        x = 'capacity in MW',
        y = 'name of powerplant',
        template = 'ggplot2',
        title = f'Rangking of Overall Power Plants in {str(country_name)}',
    )

    return plot_ranking

### callback Plot distribution
@app.callback(
    Output(component_id='plotdistribut', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot2(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]
    plot_distribut = px.box(
        gpp_indo,
        color='primary_fuel',
        y='capacity in MW',
        template='ggplot2',
        title=f'Distribution of capacity in MW in each fuel in {country_name}',
        labels={
            'primary_fuel': 'Type of Fuel'
        }
    ).update_xaxes(visible=False)

    return plot_distribut

## callback plot pie

@app.callback(
    Output(component_id='plotpie', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)
def update_plot3(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]
    agg2=pd.crosstab(
        index=gpp_indo['primary_fuel'],
        columns='No of Power Plant'
    ).reset_index()

    # visualize
    plot_pie = px.pie(
        agg2,
        values='No of Power Plant',
        names='primary_fuel',
        color_discrete_sequence=['aquamarine', 'salmon', 'plum', 'grey', 'slateblue'],
        template='ggplot2',
        hole=0.4,
        title=f'Distribution of Fuel Type in {country_name}',
        labels={
            'primary_fuel': 'Type of Fuel'
        }
    )

    return plot_pie



if __name__ == "__main__":
    app.run_server()