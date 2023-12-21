import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Create a Dash application
app = dash.Dash(__name__)

file_path = 'owid-covid-data.csv'

# Read the dataset
covid_data = pd.read_csv(file_path)

# Filter for the time range: January 1, 2021 to December 31, 2021
covid_data['date'] = pd.to_datetime(covid_data['date'])  # Ensure the date column is in date format
start_date = '2021-01-01'
end_date = '2021-12-31'
mask = (covid_data['date'] >= start_date) & (covid_data['date'] <= end_date)
filtered_data = covid_data.loc[mask]

# Select the required columns: country code, date, new cases, total cases, deaths
selected_columns = ['iso_code', 'location', 'date', 'new_cases', 'total_cases', 'new_deaths']
processed_data = filtered_data[selected_columns].copy()  # Use .copy() to create a copy

# Convert date format and sort
processed_data['date'] = pd.to_datetime(processed_data['date']).dt.strftime('%Y-%m-%d')
processed_data.sort_values('date', inplace=True)

countries = processed_data['location'].unique()
country_options = [{'label': country, 'value': country} for country in countries]

# Layout of the Dash application
app.layout = html.Div([
    # Radio buttons to select data type
    dcc.RadioItems(
        id='data-type-selector',
        options=[
            {'label': 'Total cases', 'value': 'total_cases'},
            {'label': 'Deaths', 'value': 'new_deaths'},
            {'label': 'New cases', 'value': 'new_cases'}
        ],
        value='total_cases'  # Default value
    ),
    dcc.Dropdown(
        id='country-selector',
        options=country_options,
        value=['Ireland'],  # Set the default value as a list
        multi=True  # Allow selection of multiple countries
    ),
    # Chart component for displaying the map
    dcc.Graph(id='covid-map'),
    dcc.Graph(id='country-trend')
])

@app.callback(
    Output('covid-map', 'figure'),
    [Input('data-type-selector', 'value'),
     Input('country-selector', 'value')]
)
def update_map(selected_data_type, selected_countries):
    # If no countries are selected, show all countries
    if selected_countries:
        filtered_data = processed_data[processed_data['location'].isin(selected_countries)]
    else:
        filtered_data = processed_data

    # Create a map
    fig = px.choropleth(
        filtered_data,
        locations="iso_code",
        color=selected_data_type,
        hover_name="location",
        animation_frame="date",
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"Data: {selected_data_type}",
    )
    return fig

@app.callback(
    Output('country-trend', 'figure'),
    [Input('data-type-selector', 'value'),
     Input('country-selector', 'value')]
)
def update_country_trend(selected_data_type, selected_countries):
    # Ensure a single country is selected
    if selected_countries and len(selected_countries) == 1:
        country_data = processed_data[processed_data['location'] == selected_countries[0]]
        fig = px.line(
            country_data,
            x='date',
            y=selected_data_type,
            title=f"{selected_countries[0]}: {selected_data_type} over time"
        )
    else:
        fig = px.line(title="Please select a single country to view trends.")

    return fig

# Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True)
