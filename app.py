import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.offline as py
import plotly.graph_objs as go
import plotly.express as px

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(external_stylesheets = external_stylesheets)

###### Preproc
world_cups_matches = pd.read_csv("WorldCupMatches.csv")
world_cups = pd.read_csv("WorldCups.csv")
world_cup_player = pd.read_csv("WorldCupPLayers.csv")
world_cup_player = world_cup_player.dropna()
world_cups = world_cups.dropna()
world_cups_matches = world_cups_matches.dropna()
world_cups = world_cups.replace('Germany FR', 'Germany')
world_cup_player = world_cup_player.replace('Germany FR', 'Germany')
world_cups_matches = world_cups_matches.replace('Germany FR', 'Germany')
world_cups['Attendance'] = world_cups['Attendance'].str.replace('.', '').astype('int64')
world_cups_matches['Year'] = world_cups_matches['Year'].astype('int64')

#####

features = [{'label': 'Attendance Per Cup', 'value': 'Attendance'}, 
            {'label': 'Number of Teams Per Cup', 'value': 'QualifiedTeams'}, 
            {'label': 'Number of Matchs Per Cup', 'value': 'MatchesPlayed'}, 
            {'label': 'Number of Goals Per Cup', 'value': 'GoalsScored'}]
dictByValues = {'Attendance' : 'Attendance Per Cup', 'QualifiedTeams' : 'Number of Teams Per Cup', 'MatchesPlayed' : 'Number of Matchs Per Cup', 'GoalsScored' : 'Number of Goals Per Cup'}
# years = [{'label': i, 'value': i} for i in year_cols]
# num_options = [{'label': i, 'value': i} for i in num_cols]


########Fig 2
gold = world_cups["Winner"]
silver = world_cups["Runners-Up"]
bronze = world_cups["Third"]

gold_count = pd.DataFrame.from_dict(gold.value_counts())
silver_count = pd.DataFrame.from_dict(silver.value_counts())
bronze_count = pd.DataFrame.from_dict(bronze.value_counts())
podium_count = gold_count.join(silver_count, how='outer').join(bronze_count, how='outer')
podium_count = podium_count.fillna(0)
podium_count.columns = ['WINNER', 'SECOND', 'THIRD']
podium_count = podium_count.astype('int64')
podium_count = podium_count.sort_values(by=['WINNER', 'SECOND', 'THIRD'], ascending=False)

figure_2 = go.Figure(data=[
    go.Bar(name='WINNER', x=podium_count.index, y=podium_count['WINNER']),
    go.Bar(name='SECOND', x=podium_count.index, y=podium_count['SECOND']),
    go.Bar(name='THIRD', x=podium_count.index, y=podium_count['THIRD'])
])
figure_2.update_layout(title_text='Number of podium by country')

###Fig 3
home = world_cups_matches[['Home Team Name', 'Home Team Goals', 'Year']].dropna()
away = world_cups_matches[['Away Team Name', 'Away Team Goals', 'Year']].dropna()

goal_per_country = pd.DataFrame(columns=['countries', 'goals', 'Year'])

goal_per_country = goal_per_country.append(home.rename(index=str, columns={'Home Team Name': 'countries', 'Home Team Goals': 'goals', 'Year':'Year'}))
goal_per_country = goal_per_country.append(away.rename(index=str, columns={'Away Team Name': 'countries', 'Away Team Goals': 'goals', "Year" : 'Year'}))

countries = [{'label': i, 'value': i} for i in goal_per_country['countries'].unique()]

###Fig4

years = [{'label': i, 'value': i} for i in world_cups['Year'].unique()]


app.layout = html.Div([
            html.Div([html.H1('FIFA World Cup')], className = 'row'),
             
          html.Div([dcc.Dropdown(
                                id = 'features_input',
                                options = features, value = features[0]['value'], className='twelve columns')],
                 className = 'twelve columns'),
          html.Div([
                   html.Div([dcc.Graph(id='Fig1')], className = 'twelve columns'),
            ], className = 'row'),
         html.Div([dcc.Dropdown(
                                id = 'countries_input',
                                options = countries, value = countries[0]['value'], className='twelve columns')],
                 className = 'twelve columns'),
          html.Div([
                   html.Div([dcc.Graph(id='Fig2')], className = 'twelve columns'),
            ], className = 'row'),
    
            html.Div([
                   html.Div([dcc.Graph(figure = figure_2)], className = 'twelve columns'),
            ], className = 'row'),
            
        html.Div([
        html.Div([dcc.Dropdown(id = 'countries_input2',
                                options = countries, value = countries[7]['value'])], className='four columns'),
        html.Div([dcc.Dropdown(id = 'year_input2',
                                options = years, value = years[-1]['value'])], className = 'four columns'),
        
        html.Div([html.Button(id = 'submit', n_clicks = 0, children = 'Submit')], className = 'four columns')
                 
                 ], className = 'row'),
    
        html.Div([
                   html.Div([dcc.Graph(id='Fig3')], className = 'twelve columns'),
            ], className = 'row'),
        
], className = 'container')

@app.callback(
       Output(component_id = 'Fig1', component_property = 'figure'),
        [Input(component_id = 'features_input', component_property = 'value')] 
)

def update_output(input_1):
    figure_1 = px.bar(world_cups, x='Year', y=input_1, title = dictByValues.get(input_1))
    return figure_1


@app.callback(
       Output(component_id = 'Fig2', component_property = 'figure'),
       [Input(component_id = 'countries_input', component_property = 'value')] 
)

def update_output_countries(input_2):
    data = goal_per_country[goal_per_country["countries"] == input_2]
    data = data.groupby(['Year'])['goals'].sum()
    new_data = pd.DataFrame()
    new_data['Year'] = data.index
    new_data['goals'] = data.values
    figure_2 = px.line(new_data, x='Year', y='goals', title='Number of Goals {} Per Cup'.format(input_2))
    return figure_2

@app.callback(
       Output(component_id = 'Fig3', component_property = 'figure'),
       [Input(component_id = 'submit', component_property = 'n_clicks')],
       [State(component_id = 'countries_input2', component_property = 'value'),
        State(component_id = 'year_input2', component_property = 'value')]
)

def update_countries_year(clicks, input_3, input_4):
    home_team = world_cups_matches[(world_cups_matches['Home Team Name'] == input_3)]
    home_team = home_team[home_team['Year'] == np.int(input_4)]
    away_team = world_cups_matches[world_cups_matches['Away Team Name'] == input_3]
    away_team = away_team[away_team['Year'] == np.int(input_4)]
    df1 = pd.DataFrame()
    df1['countries'] = home_team['Away Team Name']
    df1['sub_goals'] = home_team['Away Team Goals'] - home_team['Home Team Goals']
    df2 = pd.DataFrame()
    df2['countries'] = away_team['Home Team Name']
    df2['sub_goals'] = away_team['Home Team Goals'] - away_team['Away Team Goals']
    frames = [df1, df2]
    result = pd.concat(frames)
    result2 = result.groupby(['countries'])['sub_goals'].sum()
    
    data = go.Choropleth(
    locations = result2.index,
    locationmode = 'country names',
    z = result2.values,
    marker = go.choropleth.Marker(
        line = go.choropleth.marker.Line(
            color = 'rgb(255, 255, 255)',
            width = 1.5,
        )
    ),
    colorbar = go.choropleth.ColorBar(
        title = 'Score'
        )
    )

    layout = go.Layout(
        geo = go.layout.Geo(
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)'

        )
    )


    fig = go.Figure(data = data, layout = layout)
    return fig
    
    
if __name__ == '__main__':
    app.run_server(debug = True)