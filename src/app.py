import dash
from dash import Dash, dcc, html, dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output




# Style for tiles
tile_style = {
    'background-color': '#f0f0f0',
    'border-radius': '10px',
    'padding': '5px',
    'margin': '5px',
    'text-align': 'center',
    'display': 'inline-block',
    'width': '80%'
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

header_style = {
    'margin-bottom': '10px'  # Adjust the value as needed for desired spacing
}

def get_color(value):
    if value is None:
        return "#000000"  # Default to black if data is not available
    return "#ff0000" if value < 0 else "#008000"  # Red for negative, green for positive

def format_number(value):
    if value is None:
        return 'N/A'
    return f"{value:,}".replace(",", ".")


# Load data
df = pd.read_csv('pricedata7.csv')

df = df[~df['Kategorie'].isin(['Bus', 'Wohnwagen'])]

# Data preprocessing
data = df
data['Verkauf in'] = pd.to_datetime(data['Verkauf in'])
data['Quarter'] = data['Verkauf in'].dt.to_period('Q')




colors = ['#F97A1F', '#C91D42', '#1DC9A4', '#141F52']

# Define a consistent category order
category_order = sorted(data['Kategorie'].apply(str).unique())

# Processing for Line Chart
category_grouped = data.groupby(['Kategorie', 'Quarter']).agg({'Verkaufspreis': 'median'}).reset_index()
category_grouped.sort_values('Quarter', inplace=True)
last_five_quarters = category_grouped['Quarter'].unique()[-5:]
category_grouped = category_grouped[category_grouped['Quarter'].isin(last_five_quarters)]

# Creating Line Chart
category_line_chart_figure = go.Figure()

for i, category in enumerate(category_order):
    category_data = category_grouped[category_grouped['Kategorie'] == category]
    category_line_chart_figure.add_trace(go.Scatter(
        x=category_data['Quarter'].astype(str),
        y=category_data['Verkaufspreis'],
        mode='lines+markers',
        name=category,
        line=dict(color=colors[i % len(colors)])
    ))



y_values = list(range(0, 100001, 10000))  # Convert range to list
ticktext = [str(int(value / 1000)) for value in y_values]  # Convert to simpler numbers

category_line_chart_figure.update_layout(
    xaxis_title='Quartal',
    yaxis_title='Medianpreis (in Tsd)',
    legend=dict(
        orientation='h',
        x=0.5,
        y=-0.3,
        xanchor='center',
        yanchor='top'
    ),
    margin=dict(l=20, r=20, t=20, b=20),
    font=dict(family='Roboto Condensed', size=14),
    yaxis=dict(
        tickvals=y_values,
        ticktext=ticktext
    )
)

data['Verkauf in'] = pd.to_datetime(data['Verkauf in'])
data['Quarter'] = pd.PeriodIndex(data['Verkauf in'].dt.to_period('Q'), freq='Q')
last_five_quarters = data['Quarter'].drop_duplicates().sort_values()[-5:]
data_last_five_quarters = data[data['Quarter'].isin(last_five_quarters)]

# Adjusting to count the number of sales per category per quarter instead of summing sales price
quarterly_sales_count = data_last_five_quarters.groupby(['Quarter', 'Kategorie']).size().reset_index(name='Anzahl Verkäufe')
quarterly_totals_count = quarterly_sales_count.groupby('Quarter')['Anzahl Verkäufe'].sum().reset_index()

# Merging the count data with total counts for each quarter to calculate percentages
merged_data_count = pd.merge(quarterly_sales_count, quarterly_totals_count, on='Quarter', suffixes=('', '_total'))
merged_data_count['Percentage'] = (merged_data_count['Anzahl Verkäufe'] / merged_data_count['Anzahl Verkäufe_total']) * 100

# Creating Stacked Bar Chart based on sales count
stacked_bar_chart_figure = go.Figure()

for i, category in enumerate(category_order):
    category_data = merged_data_count[merged_data_count['Kategorie'] == category]
    stacked_bar_chart_figure.add_trace(go.Bar(
        name=category,
        x=category_data['Quarter'].astype(str),
        y=category_data['Percentage'],
        text=category_data['Percentage'].apply(lambda x: f'{x:.0f}%'),
        textposition='inside',
        marker_color=colors[i % len(colors)]
    ))

stacked_bar_chart_figure.update_layout(
    barmode='stack',
    xaxis=dict(
        title='Quartal',
        type='category'
    ),
    yaxis=dict(
        title='Prozentualer Anteil (%)',
        tickformat=',d'
    ),
    legend=dict(
        orientation='h',
        x=0.5,
        y=-0.3,
        xanchor='center',
        yanchor='top'
    ),
    legend_title_text='Fahrzeugkategorie',
    margin=dict(l=20, r=20, t=20, b=20),
    font=dict(family='Roboto Condensed', size=14) # Set font for the entire layout
)


# Group by vehicle age category and quarter
age_cat_grouped = data.groupby(['fahrzeugalter_cat', 'Quarter']).agg({'Verkaufspreis': 'median'}).reset_index()
age_cat_grouped.sort_values('Quarter', inplace=True)
last_five_quarters = age_cat_grouped['Quarter'].unique()[-5:]
age_cat_grouped = age_cat_grouped[age_cat_grouped['Quarter'].isin(last_five_quarters)]

# Create line chart for vehicle age categories
vehicle_age_line_chart_figure = go.Figure()
#age_order = sorted(data['fahrzeugalter_cat'].unique())
age_order = ["Bis 2 Jahre", "2 - 4 Jahre", "4 - 6 Jahre", "6 Jahre und älter"]

for i, age_cat in enumerate(age_order):
    age_data = age_cat_grouped[age_cat_grouped['fahrzeugalter_cat'] == age_cat]
    vehicle_age_line_chart_figure.add_trace(go.Scatter(
        x=age_data['Quarter'].astype(str),
        y=age_data['Verkaufspreis'],
        mode='lines+markers',
        name=age_cat,
        line=dict(color=colors[i % len(colors)])
    ))

y_values = list(range(0, 100001, 10000))  # Convert range to list
ticktext = [str(int(value / 1000)) for value in y_values]  # Convert to simpler numbers

vehicle_age_line_chart_figure.update_layout(
    xaxis_title='Quartal',
    yaxis_title='Medianpreis (in Tsd)',
    legend=dict(
        orientation='h',
        x=0.5,
        y=-0.3,
        xanchor='center',
        yanchor='top'
    ),
    margin=dict(l=20, r=20, t=20, b=70),
    font=dict(family='Roboto Condensed', size=14)
    # Removed manual yaxis tickvals and ticktext to allow automatic scaling
)





# Filter the data for the last five quarters
# Data preprocessing for vehicle age categories
data['Verkauf in'] = pd.to_datetime(data['Verkauf in'])
data['Quarter'] = pd.PeriodIndex(data['Verkauf in'].dt.to_period('Q'), freq='Q')
last_five_quarters = data['Quarter'].drop_duplicates().sort_values()[-5:]
data_last_five_quarters = data[data['Quarter'].isin(last_five_quarters)]

# Adjusting to count the number of sales per vehicle age category per quarter
age_cat_sales_count = data_last_five_quarters.groupby(['Quarter', 'fahrzeugalter_cat']).size().reset_index(name='Anzahl Verkäufe')
quarterly_totals_count = age_cat_sales_count.groupby('Quarter')['Anzahl Verkäufe'].sum().reset_index()

# Merging the count data with total counts for each quarter to calculate percentages
merged_data_age_count = pd.merge(age_cat_sales_count, quarterly_totals_count, on='Quarter', suffixes=('', '_total'))
merged_data_age_count['Percentage'] = (merged_data_age_count['Anzahl Verkäufe'] / merged_data_age_count['Anzahl Verkäufe_total']) * 100

# Creating Stacked Bar Chart based on sales count for vehicle age categories
vehicle_age_stacked_bar_figure = go.Figure()


for i, age_cat in enumerate(age_order):
    age_cat_data = merged_data_age_count[merged_data_age_count['fahrzeugalter_cat'] == age_cat]
    vehicle_age_stacked_bar_figure.add_trace(go.Bar(
        name=age_cat,
        x=age_cat_data['Quarter'].astype(str),
        y=age_cat_data['Percentage'],
        text=age_cat_data['Percentage'].apply(lambda x: f'{x:.0f}%'),
        textposition='inside',
        marker_color=colors[i % len(colors)]
    ))

# Update layout for the stacked bar chart to reflect counts-based percentages
vehicle_age_stacked_bar_figure.update_layout(
    barmode='stack',
    xaxis=dict(
        title='Quartal',
        type='category'
    ),
    yaxis=dict(
        title='Prozentualer Anteil (%)',
        tickformat=',d'
    ),
    legend=dict(
        orientation='h',
        x=0.5,
        y=-0.3,
        xanchor='center',
        yanchor='top',
        title='Fahrzeugalter Kategorie'
    ),
    margin=dict(l=20, r=20, t=20, b=20),
    font=dict(family='Roboto Condensed', size=14)
)















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

        html.Div([
        html.Div([
            html.H2("Performance-Dashboard: CARAVANING ", style={'textAlign': 'left', 'margin-top': '20px'})
        ], style={'width': '70%', 'display': 'inline-block'}),

        # Alert section
        html.Div(id='data-alert', style={'width': '30%', 'display': 'inline-block', 'textAlign': 'right'})
    ], style={'display': 'flex', 'width': '100%'}),

    # Tiles row with 4 tiles now
        html.Div([
            html.Div('Tile 1', id='tile-1', style=tile_style),
            html.Div('Tile 2', id='tile-2', style=tile_style),
            html.Div('Tile 3', id='tile-3', style=tile_style),
            html.Div('Tile 4', id='tile-4', style=tile_style)  # Added a fourth tile
        ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '100%'}),


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
            ], style={'width': '33.33%', 'display': 'inline-block', 'padding': '10px'}),
            
           
            # Dropdown for Alter des Fahrzeugs
            html.Div([
                html.H3('Alter des Fahrzeugs', style={'textAlign': 'center'}),
                dcc.Dropdown(
                    id='age-cat-dropdown',
                    options=[{'label': k, 'value': k} for k in data['fahrzeugalter_cat'].unique()] + [{'label': 'Total', 'value': 'Total'}],
                    value='Total',
                    style={'width': '100%', 'margin-right': '10px'}
                )
            ], style={'width': '33.33%', 'display': 'inline-block', 'padding': '10px'}),


            html.Div([
                html.H3('Region', style={'textAlign': 'center'}),
                dcc.Dropdown(
                    id='region-dropdown',
                    options=[{'label': k, 'value': k} for k in data['region'].dropna().unique()] + [{'label': 'Total', 'value': 'Total'}],
                    value='Total',
                    style={'width': '100%', 'margin-right': '10px'}
                ),
            ], style={'width': '33.33%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'display': 'flex', 'width': '100%'}),


        
        html.Div([
        # Column for the graph
            html.Div([
                # Price development heading
                html.H2("Preisentwicklung seit Q4/2022", style={'textAlign': 'center'}),
                # Graph
                dcc.Graph(id='price-graph'),
                # Number of entries display
                html.Div(id='num-entries', style={'font-family': 'Roboto Condensed'})
            ], style={'width': '60%', 'display': 'inline-block'}),  # Adjust width as needed

            # Column for the commentary
            html.Div([
                html.H3("Kommentarbereich", style={'textAlign': 'center'}),
                # You can replace this with any component you like
                html.P("""Der größte Gewinn liegt im Einkauf. Eine wohlüberlegte Ankaufsstrategie ist das A und O, um Margen zu maximieren. Hier zeigt sich die Stärke des PRICEANALYZERs, der durch detaillierte Marktkenntnisse – aufgeschlüsselt nach Fahrzeugtyp, Alter und Kilometerstand – den Einkauf entscheidend optimiert. 
Der signifikante Rückgang der Einkaufspreise um 14,5% gegenüber dem Vorjahresquartal öffnet weitreichende Möglichkeiten für Händler und andere Marktbeteiligte, ihre Rentabilität zu steigern. Der PRICEANALYZER wird damit zur zentralen Informationsquelle, die Transparenz schafft und es erlaubt, auf der Basis solider Daten Risiken zu minimieren und Gewinnpotenziale zu maximieren.
""", style={'padding': '10px'}),
                # Add more components here as needed
            ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'top'})  # Adjust width as needed
        ], style={'display': 'flex', 'width': '100%'}),

    html.Div(style={'height': '20px'}),
    html.Img(src='assets/Fahrzeugkategorie_Block.jpg'),

    html.Div([
        # Column for the line chart
        html.Div([
            dcc.Graph(
                id='category_line_chart',
                figure=category_line_chart_figure
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),

        # Column for the stacked bar chart
        html.Div([
            dcc.Graph(
                id='stacked_bar_chart',
                figure=stacked_bar_chart_figure
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'width': '100%', 'margin-top': '20px'}),


       html.Div(style={'height': '20px'}),
    html.Img(src='assets/Fahrzeugalter_Block.jpg'),

    html.Div([
        # Column for the line chart
        html.Div([
            dcc.Graph(
                id='vehicle_age_line_chart',
                figure=vehicle_age_line_chart_figure
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),

        # Column for the stacked bar chart
        html.Div([
            dcc.Graph(
                id='vehicle_age_stacked_bar',
                figure=vehicle_age_stacked_bar_figure
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'width': '100%', 'margin-top': '20px'}),








    ], style={'fontFamily': 'Roboto Condensed', 'maxWidth': '1000px', 'margin': '0 auto'}),

    

])

# New callback to update the tiles based on dropdown selections
@app.callback(
    [Output('tile-1', 'children'),
     Output('tile-2', 'children'),
     Output('tile-3', 'children'),
     Output('tile-4', 'children')],
    [Input('category-dropdown', 'value'),
     Input('age-cat-dropdown', 'value'), 
     Input('region-dropdown', 'value')]
)
def update_tiles(selected_category, selected_age_cat, selected_region):
    # Filter data based on dropdown values
    filtered_data = data.copy()
    if selected_category != 'Total':
        filtered_data = filtered_data[filtered_data['Kategorie'] == selected_category]
    if selected_age_cat != 'Total':
        filtered_data = filtered_data[filtered_data['fahrzeugalter_cat'] == selected_age_cat]
    if selected_region != 'Total':
        filtered_data = filtered_data[filtered_data['region'] == selected_region]


    # Calculate Median-Verkaufspreis for Q4 2023
    q4_2023_data = filtered_data[filtered_data['Quarter'] == '2023Q4']
    median_price_2023 = round(q4_2023_data['Verkaufspreis'].median())

    # Calculate percentage difference vs. Q4 2022
    q4_2022_data = filtered_data[filtered_data['Quarter'] == '2022Q4']
    median_price_2022 = q4_2022_data['Verkaufspreis'].median()
    percentage_diff_2022 = ((median_price_2023 - median_price_2022) / median_price_2022) * 100 if median_price_2022 else None

    # Calculate percentage difference vs. previous quarter
    current_quarter_period = pd.Period('2023Q4', freq='Q')  # Ändern Sie dies entsprechend, um das aktuelle Quartal dynamisch zu bestimmen
    previous_quarter_period = current_quarter_period - 1
    previous_quarter = previous_quarter_period.strftime('Q%q/%Y')
    
    previous_q_data = filtered_data[filtered_data['Quarter'] == previous_quarter_period]
    median_price_previous = previous_q_data['Verkaufspreis'].median()
    percentage_diff_previous = ((median_price_2023 - median_price_previous) / median_price_previous) * 100 if median_price_previous else None



    # Calculate percentage difference between Verkaufspreis and Wunschpreis for the latest quarter
    median_wunschpreis_2023 = q4_2023_data['Wunschpreis'].median()
    percentage_diff_wunschpreis = ((median_price_2023 - median_wunschpreis_2023) / median_wunschpreis_2023) * 100 if median_wunschpreis_2023 else None

    number_style = {
        'font-size': '20px',  # Increase font size as needed
        'font-weight': 'bold'  # Optional: make the font bold
    }

    # Formatting tile contents
    tile_1_content = html.Div([
    html.Div(html.Strong("Median-Verkaufspreis (Q4/2023):"), style={'margin-bottom': '10px'}),
    html.Div(format_number(median_price_2023) + " €" if median_price_2023 else 'Data not available', style=number_style)
], style=tile_style)

    tile_2_content = html.Div([
        html.Div(html.Strong("Proz. Differenz (vs. Q4/2022):"), style={'margin-bottom': '10px'}),
        html.Div(html.Span(f"{percentage_diff_2022:.2f}%", style={'color': get_color(percentage_diff_2022)}) if percentage_diff_2022 is not None else 'Data not available', style=number_style)
    ], style=tile_style)

    tile_3_content = html.Div([
        html.Div(html.Strong(f"Proz. Differenz (vs. {previous_quarter}):"), style={'margin-bottom': '10px'}),
        html.Div(html.Span(f"{percentage_diff_previous:.2f}%", style={'color': get_color(percentage_diff_previous)}) if percentage_diff_previous is not None else 'Data not available', style=number_style)
    ], style=tile_style)

    tile_4_content = html.Div([
        html.Div(html.Strong("Ratio (Angebots- zu Verkaufspreis):"), style={'margin-bottom': '10px'}),
        html.Div(html.Span(f"{percentage_diff_wunschpreis:.2f}%", style={'color': get_color(percentage_diff_wunschpreis)}) if percentage_diff_wunschpreis is not None else 'Data not available', style=number_style)
    ], style=tile_style)

    return tile_1_content, tile_2_content, tile_3_content, tile_4_content




@app.callback(
    [Output('price-graph', 'figure'),
     Output('num-entries', 'children')],
    [Input('category-dropdown', 'value'),
     Input('age-cat-dropdown', 'value'),
     Input('region-dropdown', 'value')]
)



def update_graph(selected_category, selected_age_cat, selected_region):
    # Filter data based on dropdown values
    filtered_data = data.copy()
    if selected_category != 'Total':
        filtered_data = filtered_data[filtered_data['Kategorie'] == selected_category]
    if selected_age_cat != 'Total':
        filtered_data = filtered_data[filtered_data['fahrzeugalter_cat'] == selected_age_cat]
    if selected_region != 'Total':
        filtered_data = filtered_data[filtered_data['region'] == selected_region]

    # Group by quarter after filtering
    filtered_quarterly = filtered_data.groupby('Quarter').agg({'Verkaufspreis': 'median'}).reset_index()

    # Identify the last 5 quarters in the dataset
    last_5_quarters = filtered_quarterly['Quarter'].unique()[-5:]

    # Filter data to only include these quarters
    filtered_quarterly = filtered_quarterly[filtered_quarterly['Quarter'].isin(last_5_quarters)]
    

    # Count the number of entries
    num_entries = len(filtered_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_quarterly['Quarter'].astype(str), y=filtered_quarterly['Verkaufspreis'],
                             mode='lines+markers', line=dict(color='#b22122', width=4), name='Verkaufspreis'))

    # Dynamically adjust y-axis range
    min_price = filtered_quarterly['Verkaufspreis'].min()
    max_price = filtered_quarterly['Verkaufspreis'].max()
    y_axis_min = max(min_price - (60000 - (max_price - min_price)) // 2, 0)
    y_axis_max = y_axis_min + 60000

    # Round y_axis_min to nearest ten thousand
    y_axis_min_rounded = int(round(y_axis_min, -4))

    # Generate y-values for the range, starting from the rounded minimum
    y_values = list(range(y_axis_min_rounded, y_axis_min_rounded + 60001, 10000))
    ticktext = [str(int(value / 1000)) for value in y_values]

    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=y_values,
            ticktext=ticktext,
            range=[y_axis_min, y_axis_min + 60000]
        ),
        margin=dict(l=20, r=20, t=10, b=20),
        legend=dict(
            x=0.01,
            y=0.99,
            bordercolor="Black",
            borderwidth=2,
            orientation="h"
        ),
        font=dict(family='Roboto Condensed', size=14)  # Set the font globally for the figure
    )

    # Return the figure and the number of entries
    return fig, f"n = {num_entries}"



@app.callback(
    Output('data-alert', 'children'),
    [Input('category-dropdown', 'value'),
     Input('age-cat-dropdown', 'value'),
     Input('region-dropdown', 'value')]
)
def update_data_alert(selected_category, selected_age_cat, selected_region):
    filtered_data = data.copy()
    # Apply the same filters as in your other callbacks
    if selected_category != 'Total':
        filtered_data = filtered_data[filtered_data['Kategorie'] == selected_category]
    if selected_age_cat != 'Total':
        filtered_data = filtered_data[filtered_data['fahrzeugalter_cat'] == selected_age_cat]
    if selected_region != 'Total':
        filtered_data = filtered_data[filtered_data['region'] == selected_region]

    # Filter data for Q4
    q4_data = filtered_data[filtered_data['Quarter'] == '2023Q4']  # Adjust the year as needed

    # Check the number of entries in Q4
    if len(q4_data) < 10:
        return html.Div('Hinweis: Für das letzte Quartal liegen uns zu wenige Daten vor. Bitte wählen Sie weniger Parameter.', 
                        style={'color': 'red', 
                               'fontWeight': 'bold', 
                               'fontSize': '14px', 
                               'display': 'flex', 
                               'alignItems': 'center', 
                               'justifyContent': 'center',
                               'height': '100%'})
    return ''





# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)
