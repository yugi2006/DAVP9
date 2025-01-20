import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import io
import flask

data = pd.read_csv('playersdata7.csv')
df = pd.DataFrame(data)

app = dash.Dash(__name__)
server = app.server  

price_per_team = df.groupby('Team').agg({'Price(LAKHS)': 'sum'}).reset_index()
bar_fig = px.bar(price_per_team, x='Team', y='Price(LAKHS)', title='Total Price per Team')

player_distribution = df['Team'].value_counts().reset_index()
player_distribution.columns = ['Team', 'Players']
pie_fig = px.pie(player_distribution, names='Team', values='Players', title='Player Distribution Across Teams')

app.layout = html.Div([
    html.H1("Kabaddi Players Dashboard", style={'text-align': 'center'}),

    html.Div([
        html.Div([
            dcc.Graph(figure=bar_fig, id='team-bar-chart'),  # Bar chart
        ], className="six columns"),

        html.Div([
            dcc.Graph(figure=pie_fig),  # Pie chart
        ], className="six columns"),
    ], className="row"),

    html.Div([
        html.H3("Select a Team to View Data and Download", style={'text-align': 'center'}),
        dcc.Dropdown(
            id='team-dropdown',
            options=[{'label': team, 'value': team} for team in df['Team'].unique()],
            placeholder='Select a Team',
            style={'width': '60%', 'margin': 'auto'}
        ),
    ]),

    html.Div([
        html.H3("Team Details", style={'text-align': 'center'}),
        html.Div(id='team-details'),  # Table to display team data
        html.Div(id='team-line-plot')  # Line plot for the selected team
    ]),

    
    html.Div([
        html.Button("Download Team Data", id="download-button", style={'margin': '20px auto', 'display': 'block'}),
        dcc.Download(id="team-data-download")  # Component to download data
    ])
])

@app.callback(
    [Output('team-details', 'children'),
     Output('team-line-plot', 'children')],
    Input('team-dropdown', 'value')
)
def display_team_details(team_name):
    if not team_name:
        return html.Div([
            html.H4("Please select a team to view details and the line plot.")
        ]), None  # No line plot when no team is selected

    team_data = df[df['Team'] == team_name]

    table_header = [
        html.Tr([html.Th(col) for col in team_data.columns])
    ]
    table_body = [
        html.Tr([html.Td(team_data.iloc[i][col]) for col in team_data.columns]) for i in range(len(team_data))
    ]

    line_fig = px.line(team_data, x='Player', y='Price(LAKHS)', title=f'Price per Player in {team_name}', markers=True)

    return html.Table(table_header + table_body, style={'width': '80%', 'margin': 'auto'}), dcc.Graph(figure=line_fig)

@app.callback(
    Output('team-data-download', 'data'),
    Input('download-button', 'n_clicks'),
    Input('team-dropdown', 'value'),
    prevent_initial_call=True
)
def download_team_data(n_clicks, team_name):
    if not team_name:
        return None  # No team selected
    team_data = df[df['Team'] == team_name]
    return dcc.send_data_frame(team_data.to_csv, f"{team_name}_data.csv", index=False)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
