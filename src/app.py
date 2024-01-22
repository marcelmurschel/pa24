import dash
from dash import Dash, dcc, html, dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# Style for tiles
tile_style = {
    'background-color': '#f0f0f0',
    'border-radius': '10px',
    'padding': '20px',
    'margin': '10px',
    'text-align': 'center',
    'display': 'inline-block',
    'width': '30%'
}

table_container_style = {
    'background-color': '#f0f0f0',  # light grey background
    'border-radius': '10px',        # rounded borders
    'padding': '20px',              # some padding inside the container
    'margin': '10px auto',          # margin around the container, auto for horizontal centering
    'maxWidth': '1000px',           # maximum width of the container
}

data_table_style = {
    'fontFamily': 'Roboto Condensed',
}

# Style for the data table header
data_table_header_style = {
    'fontFamily': 'Roboto Condensed',
    'textAlign': 'center',
    'margin-top': '50px',
    'padding': '0px'
}

# Load data
df = pd.read_csv('pricedata.csv')

# Data preprocessing
data = df
data['Verkauf in'] = pd.to_datetime(data['Verkauf in'])
data['Quarter'] = data['Verkauf in'].dt.to_period('Q')

# Creating the Dash app
app = Dash(__name__)
server = app.server

# App layout
app.layout = html.Div([
    # External Google Font stylesheet
    html.Link(
        rel='stylesheet',
        href='https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;700&display=swap'
    ),
    # Content div
    html.Div([
        html.Img(src='assets/Header_PriceAnalyzer.jpg'),
        # Dropdowns
        html.Div([
            # Dropdown for Fahrzeugtyp
            html.Div([
                html.H3('Fahrzeugtyp', style={'textAlign': 'center'}),
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': k, 'value': k} for k in data['Kategorie'].dropna().unique()] + [{'label': 'Total', 'value': 'Total'}],
                    value='Total',
                    style={'width': '100%', 'margin-right': '10px'}
                ),
            ], style={'width': '32%', 'display': 'inline-block', 'padding': '10px'}),

            # Dropdown for Kilometerstand
            html.Div([
                html.H3('Kilometerstand', style={'textAlign': 'center'}),
                dcc.Dropdown(
                    id='km-cat-dropdown',
                    options=[{'label': k, 'value': k} for k in data['Kilometer_cat'].unique()] + [{'label': 'Total', 'value': 'Total'}],
                    value='Total',
                    style={'width': '100%', 'margin-right': '10px'}
                ),
            ], style={'width': '32%', 'display': 'inline-block', 'padding': '10px'}),

            # Dropdown for Alter des Fahrzeugs
            html.Div([
                html.H3('Alter des Fahrzeugs', style={'textAlign': 'center'}),
                dcc.Dropdown(
                    id='age-cat-dropdown',
                    options=[{'label': k, 'value': k} for k in data['fahrzeugalter_cat'].unique()] + [{'label': 'Total', 'value': 'Total'}],
                    value='Total',
                    style={'width': '100%', 'margin-right': '10px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'padding': '10px'})
        ], style={'display': 'flex', 'width': '100%'}),

        # Tiles row
        html.Div([
            html.Div('Tile 1', id='tile-1', style=tile_style),
            html.Div('Tile 2', id='tile-2', style=tile_style),
            html.Div('Tile 3', id='tile-3', style=tile_style)
        ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '100%'}),

        # Price development heading
        html.Div([
            html.H2("Preisentwicklung seit Q1/2022", style={'textAlign': 'center', 'margin-top': '50px', 'padding': '0px'})
        ]),

        # Graph
        dcc.Graph(id='price-graph'),
        # Number of entries display
        html.Div(id='num-entries', style={'font-family': 'Roboto Condensed'})
    ], style={'fontFamily': 'Roboto Condensed', 'maxWidth': '1000px', 'margin': '0 auto'}),

    # DataTable and Download Button
    html.Div([
        html.H2("Medianpreise pro Quartal", style=data_table_header_style),
       

        dash_table.DataTable(
            id='price-table',
            columns=[{"name": i, "id": i} for i in ['Quarter', 'Median Price']],
            data=[],
            style_table={'margin': 'auto', **data_table_style},
            style_data=data_table_style,  # Apply the font style to the data cells
            export_format='csv',
            export_headers='display',
            merge_duplicate_headers=True
        ),

        html.Button("Download Data", id="btn-download", n_clicks=0),
        dcc.Download(id='download-data')
    ], style=table_container_style)
])

# New callback to update the tiles based on dropdown selections
@app.callback(
    [Output('tile-1', 'children'),
     Output('tile-2', 'children'),
     Output('tile-3', 'children'),],
    [Input('category-dropdown', 'value'),
     Input('km-cat-dropdown', 'value'),
     Input('age-cat-dropdown', 'value')]
)



def update_tiles(selected_category, selected_km_cat, selected_age_cat):
    # Filter data based on dropdown values
    filtered_data = data.copy()
    if selected_category != 'Total':
        filtered_data = filtered_data[filtered_data['Kategorie'] == selected_category]
    if selected_km_cat != 'Total':
        filtered_data = filtered_data[filtered_data['Kilometer_cat'] == selected_km_cat]
    if selected_age_cat != 'Total':
        filtered_data = filtered_data[filtered_data['fahrzeugalter_cat'] == selected_age_cat]

    # Filter for Quarter 4 of 2023
    q4_2023_data = filtered_data[filtered_data['Quarter'] == '2023Q4']
    median_price_2023 = q4_2023_data['Verkaufspreis'].median()

    # Filter for Quarter 4 of 2022
    q4_2022_data = filtered_data[filtered_data['Quarter'] == '2022Q4']
    median_price_2022 = q4_2022_data['Verkaufspreis'].median()

    # Calculate percentage difference
    if median_price_2022 and median_price_2023:
        percentage_diff = ((median_price_2023 - median_price_2022) / median_price_2022) * 100
    else:
        percentage_diff = None

    # Number of records for Q4 2023
    num_records = len(q4_2023_data)

    # Formatting the tile content with bold labels and values on new lines
    tile_1_content = html.Div([
        html.Strong("Median-Verkaufspreis (Q4/2023):"),
        html.Br(),
        f"{median_price_2023:.2f} €" if median_price_2023 else 'Data not available'
    ])

    tile_2_content = html.Div([
        html.Strong("Proz. Differenz (vs. Q4/2022):"),
        html.Br(),
        f"{percentage_diff:.2f}%" if percentage_diff is not None else 'Data not available'
    ])

    tile_3_content = html.Div([
        html.Strong("Anzahl der Fälle:"),
        html.Br(),
        f"{num_records}"
    ])

    return tile_1_content, tile_2_content, tile_3_content




@app.callback(
    [Output('price-graph', 'figure'),
     Output('num-entries', 'children')],
    [Input('category-dropdown', 'value'),
     Input('km-cat-dropdown', 'value'),
     Input('age-cat-dropdown', 'value')]
)



def update_graph(selected_category, selected_km_cat, selected_age_cat):
    # Filter data based on dropdown values
    filtered_data = data.copy()
    if selected_category != 'Total':
        filtered_data = filtered_data[filtered_data['Kategorie'] == selected_category]
    if selected_km_cat != 'Total':
        filtered_data = filtered_data[filtered_data['Kilometer_cat'] == selected_km_cat]
    if selected_age_cat != 'Total':
        filtered_data = filtered_data[filtered_data['fahrzeugalter_cat'] == selected_age_cat]

    # Group by quarter after filtering
    filtered_quarterly = filtered_data.groupby('Quarter').agg({'Verkaufspreis': 'median', 'Wunschpreis': 'median'}).reset_index()

    # Count the number of entries
    num_entries = len(filtered_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_quarterly['Quarter'].astype(str), y=filtered_quarterly['Verkaufspreis'],
                             mode='lines+markers', line=dict(color='#b22122', width=4), name='Verkaufspreis'))
    fig.add_trace(go.Scatter(x=filtered_quarterly['Quarter'].astype(str), y=filtered_quarterly['Wunschpreis'],
                             mode='lines+markers', line=dict(color='#141F52', width=4), name='Wunschpreis'))

    # Set fixed range for y-axis and update axis labels
    fig.update_layout(
        yaxis_range=[30000, 80000],
        yaxis=dict(
            tickmode='array',
            tickvals=[10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
        ),
        margin=dict(l=20, r=20, t=10, b=20),  # Adjust these values as needed

        # Positioning the legend inside the graph
        legend=dict(
            x=0.01,  # X position of the legend (0 is left, 1 is right)
            y=0.99,  # Y position of the legend (0 is bottom, 1 is top)
            bordercolor="Black",
            borderwidth=2,
            orientation="h"  # Horizontal orientation of the legend items
        )
    )

    # Return the figure and the number of entries
    return fig, f"n = {num_entries}"


@app.callback(
    Output('price-table', 'data'),
    [Input('category-dropdown', 'value'),
     Input('km-cat-dropdown', 'value'),
     Input('age-cat-dropdown', 'value')]
)
def update_table(selected_category, selected_km_cat, selected_age_cat):
    # Filter data based on dropdown values
    filtered_data = data.copy()
    if selected_category != 'Total':
        filtered_data = filtered_data[filtered_data['Kategorie'] == selected_category]
    if selected_km_cat != 'Total':
        filtered_data = filtered_data[filtered_data['Kilometer_cat'] == selected_km_cat]
    if selected_age_cat != 'Total':
        filtered_data = filtered_data[filtered_data['fahrzeugalter_cat'] == selected_age_cat]

    # Calculate median prices per quarter
    median_prices = filtered_data.groupby('Quarter')['Verkaufspreis'].median().reset_index()
    median_prices.rename(columns={'Verkaufspreis': 'Median Price'}, inplace=True)

    # Convert Period to string for JSON serialization
    median_prices['Quarter'] = median_prices['Quarter'].astype(str)

    # Convert DataFrame to a dictionary for the DataTable
    return median_prices.to_dict('records')


# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)
