import dash
from flask import Flask
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine,text
import pandas as pd
import plotly_express as px


# Create a Flask web server
server = Flask(__name__)
port = 1862

# Create a Dash web application
app = Dash(__name__, server=server,external_stylesheets=[dbc.themes.BOOTSTRAP])

# Connect to the MySQL database using SQLAlchemy
engine = create_engine('mysql+pymysql://root:Matthan%40977147@localhost/generate_stats')

query = text(f"select * from generate_stats.json_daily_skills_dash where Avg_Salary != 0")
df = pd.read_sql(query, con=engine)


def region_default_graph():
    df1 = df.groupby('region')['Avg_Salary'].mean().reset_index()
    default_fig = px.bar(df1, x='region', y='Avg_Salary',color='region',labels={'region': 'Region'},color_discrete_sequence=px.colors.qualitative.Safe)
    default_fig.update_layout(title='Region-wise Average Salary', xaxis_title='Region',
                              yaxis_title='Average Salary',plot_bgcolor='#000000',font=dict(color='white'),title_x=0.5,paper_bgcolor='#000000')
    return default_fig

def country_default_graph():
    df1 = df.groupby('country')['Avg_Salary'].mean().reset_index()
    df1['Avg_Salary'] = df1['Avg_Salary'].fillna(0)

    default_fig = px.scatter_geo(df1,locations='country',locationmode='country names',color='Avg_Salary',size='Avg_Salary',size_max=50, color_continuous_scale="Viridis",hover_name='country')
    default_fig.update_layout(title='Country-wise Average Salary', plot_bgcolor='#000000', font=dict(color='white'),
                              title_x=0.5, paper_bgcolor='#000000')


    return default_fig

def industry_default_graph():
    df1 = df.groupby('industry')['Avg_Salary'].mean().reset_index()

    default_fig = px.treemap(df1,path=['industry'],values='Avg_Salary',color='industry',color_discrete_sequence=px.colors.qualitative.Prism)
    default_fig.update_layout(title='Industry-wise Average Salary',plot_bgcolor='#000000',title_x=0.5)
    return default_fig

def company_default_graph():
    df1 = df.groupby('company')['Avg_Salary'].mean().reset_index()
    default_fig = px.area(df1, x='company', y='Avg_Salary', color='company', labels={'job-role': 'Job Role', 'Avg_Salary': 'Average Salary','company': 'Company'})
    default_fig.update_layout(xaxis=dict(title='Company-wise Average Salary', showticklabels=False,showgrid=False),  yaxis=dict(showgrid=False),
                              yaxis_title='Average Salary',plot_bgcolor='#000000',title_x=0.5,font=dict(color='white'),paper_bgcolor='#000000')
    return default_fig

def role_default_graph():
    df1 = df.groupby('job-role')['Avg_Salary'].mean().reset_index()
    default_fig = px.scatter(df1, x='job-role', y='Avg_Salary', color='job-role',size='Avg_Salary',
                             labels={'job-role': 'Job Role', 'Avg_Salary': 'Average Salary'},size_max=50)
    default_fig.update_layout(xaxis=dict(title='Role-wise Average Salary', showticklabels=False,showgrid=False),yaxis=dict(showgrid=False),
                              yaxis_title='Average Salary',plot_bgcolor='#000000',title_x=0.5,font=dict(color='white'),paper_bgcolor='#000000')
    return default_fig

# Define the layout of your Dash app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Average Salary",style={'textAlign':'center'},className="mb-4"))
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Quarter", id='quarter-button', color="success",className="me-4"),
            dbc.Button("Biannual", id='biannual-button', color="warning",className="me-4"),
            dbc.Button("Annual", id='annual-button', color="danger")
            ])
        ]),
        html.Div(id='button-value', style={'display': 'none'}),
        html.Br(),
    dbc.Row([
        dbc.Col([dcc.Dropdown(id='region',options=[{'label': i, 'value': i} for i in df['region'].unique()],
                              placeholder='Select a Region')],width=6),

        dbc.Col([dcc.Dropdown(id='country',placeholder='Select a Country')],width=6)
        ]),
    html.Br(),
    dbc.Row([
        dbc.Col([dcc.Dropdown(id='industry',placeholder='Select an Industry')],width={'size': 6, 'offset': 3})
        ]),
    html.Br(),

    dbc.Row([
        dbc.Col([dcc.Dropdown(id='company',placeholder='Select a Company')],width=6),
        dbc.Col([dcc.Dropdown(id='job-role',placeholder='Select a Job-Role')],width=6)

        ]),
    html.Br(),
    dbc.Row([
        dbc.Col([dcc.Graph(id='graph1',style={'border': '1px solid black'})],width=6),
        dbc.Col([dcc.Graph(id='graph2',style={'border': '1px solid black'})],width=6)
        ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id='graph5',style={'border': '1px solid black'})])
    ]),

    dbc.Row([
        dbc.Col([dcc.Graph(id='graph3',style={'border': '1px solid black'})],width=6),
        dbc.Col([dcc.Graph(id='graph4',style={'border': '1px solid black'})],width=6)
        ])

 ])

@app.callback(
    Output('country', 'options'),
    [Input('region', 'value')]
)
def update_country_options(selected_region):
    if selected_region :
        region_countries = df[df['region'] == selected_region]['country'].unique()

    return [{'label': i, 'value': i} for i in region_countries]

@app.callback(
    Output('industry', 'options'),
    [Input('country', 'value')]
)
def update_industry_options(selected_country):
    if selected_country :
        country_industry = df[df['country'] == selected_country]['industry'].unique()

    return [{'label': i, 'value': i} for i in country_industry]

@app.callback(
    Output('company', 'options'),
    [Input('industry', 'value')]
)
def update_company_options(selected_industry):
    if selected_industry:
        industry_companies = df[df['industry'] == selected_industry]['company'].unique()

    return [{'label': i, 'value': i} for i in industry_companies]


@app.callback(
    Output('job-role', 'options'),
    [Input('company', 'value')]
)
def update_role_options(selected_company):
    if selected_company:
        company_roles = df[df['company'] == selected_company]['job-role'].unique()

    return [{'label': i, 'value': i} for i in company_roles]


@app.callback(
    [Output('button-value', 'children'),
     Output('quarter-button', 'style'),
     Output('biannual-button', 'style'),
     Output('annual-button', 'style')],
    [Input('quarter-button', 'n_clicks'),
     Input('biannual-button', 'n_clicks'),
     Input('annual-button', 'n_clicks')]
)
def update_button_value(n_clicks_quarter, n_clicks_biannual, n_clicks_annual):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == 'quarter-button':
        return 'quarter',  {}, {},{}
    elif trigger_id == 'biannual-button':
        return 'biannual', {}, {},{}
    elif trigger_id == 'annual-button':
        return 'annual', {}, {},{}



@app.callback(
    Output('graph1', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value')]
)
def region_graph(param1, param2):

    if param2 is None:
        return region_default_graph()

    query = text(f"CALL generate_stats.SalaryTrend('{(param1)}', '@region={param2},')")
    data_df = pd.read_sql(query, con=engine)
    data_df['year'] = data_df['year'].astype(str)
    df = data_df[data_df['region'] == param2]

    if param1=='quarter':
        df[['Quarter_1', 'Quarter_2', 'Quarter_3', 'Quarter_4']] = df[['Quarter_1', 'Quarter_2', 'Quarter_3', 'Quarter_4']].fillna(0)
        fig = px.bar(df, x='year',  y=['Quarter_1','Quarter_2','Quarter_3','Quarter_4'],barmode='stack',color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(title=f'Average Salary Quarterly in {param2}', xaxis_title='Year', yaxis_title='Average Salary',plot_bgcolor='#ffffff', title_x=0.5,legend_title_text='Quarter')
        fig.update_traces(text=df[['Quarter_1', 'Quarter_2', 'Quarter_3', 'Quarter_4']].values.flatten(),textposition='outside',hoverinfo='y+name')

    elif param1 == 'biannual':
        df[['BiAnnual_Q1_Q2','BiAnnual_Q3_Q4']] = df[['BiAnnual_Q1_Q2','BiAnnual_Q3_Q4']].fillna(0)
        fig = px.bar(df, x='year',  y=['BiAnnual_Q1_Q2','BiAnnual_Q3_Q4'],barmode='stack',color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(title=f'Average Salary Biannually in {param2}', xaxis_title='Year', yaxis_title='Average Salary',plot_bgcolor='#ffffff', title_x=0.5,legend_title_text='Biannual')
        fig.update_traces(text=df[['BiAnnual_Q1_Q2','BiAnnual_Q3_Q4']].values.flatten(),textposition='outside', hoverinfo='y+name')

    elif param1 == 'annual':
        df[['Annual']] = df[['Annual']].fillna(0)
        fig = px.bar(df, x='year',  y='Annual',color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(title=f'Average Salary Annually in {param2}',xaxis_title='Year', yaxis_title='Average Salary', plot_bgcolor='#ffffff',title_x=0.5,legend_title_text='Annual')
        fig.update_traces(text=df[['Annual']].values.flatten(), textposition='outside',hoverinfo='y+name')

    return fig

@app.callback(
    Output('graph2', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value')
    ]
)
def country_graph(param1,param2,param3):

    if param3 is None:
        return country_default_graph()

    query = text(f"CALL generate_stats.SalaryTrend('{(param1)}', '@region={param2},@country={param3},')")
    data_df = pd.read_sql(query, con=engine)


    if 'region' in data_df.columns and 'country' in data_df.columns:

        df2=data_df[(data_df['region']==param2) & (data_df['country']==param3)]


        if param1=='quarter':

             fig = {'data': [
                    {'x': df2['year'], 'y': df2['Quarter_1'], 'type': 'bar', 'name': 'Quarter 1','marker': {'color': '#38A3A5'}},
                    {'x': df2['year'], 'y': df2['Quarter_2'], 'type': 'bar', 'name': 'Quarter 2','marker': {'color': '#57CC99'}},
                    {'x': df2['year'], 'y': df2['Quarter_3'], 'type': 'bar', 'name': 'Quarter 3','marker': {'color': '#80ED99'}},
                    {'x': df2['year'], 'y': df2['Quarter_4'], 'type': 'bar', 'name': 'Quarter 4','marker': {'color': 'C7F9CC'}}]}
             fig['layout'] = {'xaxis': {'tickmode': 'linear', 'tickformat': '.0f', 'title': 'Year'},'yaxis': {'title': 'Average Salary'},'title': f'Average Salary Quarterly in {param3}'}

        elif param1=='biannual':
             fig = {'data': [
                    {'x': df2['year'], 'y': df2['BiAnnual_Q1_Q2'], 'type': 'bar', 'name': 'Biannual 1','marker': {'color': '#38A3A5'}},
                    {'x': df2['year'], 'y': df2['BiAnnual_Q3_Q4'], 'type': 'bar', 'name': 'Biannual 2','marker': {'color': '#57CC99'}}]}
             fig['layout'] = {'xaxis': {'tickmode': 'linear', 'tickformat': '.0f', 'title': 'Year'},'yaxis': {'title': 'Average Salary'},'title': f'Average Salary Biannually in {param3}'}

        elif param1=='annual':
            fig = {'data': [
                {'x': df2['year'], 'y': df2['Annual'], 'type': 'bar', 'name': 'Annual','marker': {'color': '#38A3A5'}}]}
            fig['layout'] = {'xaxis': {'tickmode': 'linear', 'tickformat': '.0f', 'title': 'Year'},'yaxis': {'title': 'Average Salary'},'title': f'Average Salary Annually in {param3}'}

    return fig

@app.callback(
    Output('graph5', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value'),
     Input('industry', 'value')
    ]
)
def industry_graph(param1, param2,param3,param4):

    if param4 is None:
        return industry_default_graph()

    query = text(f"CALL generate_stats.SalaryTrend('{(param1)}', '@region={param2},@country={param3},@industry={param4},')")
    data_df = pd.read_sql(query, con=engine)


    if 'region' in data_df.columns and 'country' in data_df.columns and 'industry' in data_df.columns:

        df2=data_df[(data_df['region']==param2) & (data_df['country']==param3) & (data_df['industry']==param4)]

        if param1=='quarter':

             fig = {'data': [
                 {'x': df2['year'], 'y': df2['Quarter_1'], 'mode': 'markers', 'name': 'Quarter 1','marker': {'size': df2['Quarter_1']* 0.00001, 'sizemin': 20,'color': '#45438b'}},
                 {'x': df2['year'], 'y': df2['Quarter_2'], 'mode': 'markers', 'name': 'Quarter 2','marker': {'size': df2['Quarter_2']* 0.00001, 'sizemin': 20,'color': '#064c7c'}},
                 {'x': df2['year'], 'y': df2['Quarter_3'], 'mode': 'markers', 'name': 'Quarter 3','marker': {'size': df2['Quarter_3']* 0.00001,'sizemin': 20, 'color': '#E66E60'}},
                 {'x': df2['year'], 'y': df2['Quarter_4'], 'mode': 'markers', 'name': 'Quarter 4','marker': {'size': df2['Quarter_4']* 0.00001,'sizemin': 20, 'color': '#1A8872'}}]}
             fig['layout'] = {'xaxis': {'tickmode': 'linear', 'tickformat': '.0f', 'title': 'Year'},'yaxis': {'title': 'Average Salary'},'title': f'Average Salary Quarterly in {param4}'}

        elif param1=='biannual':
             fig = {'data': [
                    {'x': df2['year'], 'y': df2['BiAnnual_Q1_Q2'], 'mode': 'markers', 'name': 'Quarter 1','marker': {'size': df2['BiAnnual_Q1_Q2']* 0.00001, 'sizemin': 10,'color': '#45438b'}},
                    {'x': df2['year'], 'y': df2['BiAnnual_Q3_Q4'], 'mode': 'markers', 'name': 'Quarter 2','marker': {'size': df2['BiAnnual_Q3_Q4']* 0.00001, 'sizemin': 10,'color': '#064c7c'}}]}
             fig['layout'] = {'xaxis': {'tickmode': 'linear', 'tickformat': '.0f', 'title': 'Year'},'yaxis': {'title': 'Average Salary'},'title': f'Average Salary Biannually in {param3}'}

        elif param1=='annual':
            fig = {'data': [
                {'x': df2['year'], 'y': df2['Annual'], 'mode': 'markers', 'name': 'Quarter 1','marker': {'size': df2['Annual']* 0.00001, 'sizemin': 10,'color': '#1A8872'}}]}
            fig['layout'] = {'xaxis': {'tickmode': 'linear', 'tickformat': '.0f', 'title': 'Year'},'yaxis': {'title': 'Average Salary'},'title': f'Average Salary Annually in {param4}'}

    return fig

@app.callback(
    Output('graph3', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value'),
     Input('industry','value'),
     Input('company', 'value')
    ]
)
def company_graph(param1, param2,param3,param4,param5):

    if param5 is None:
        return company_default_graph()

    query = text(f"CALL generate_stats.SalaryTrend('{(param1)}', '@region={param2},@country={param3},@industry={param4},@company={param5},')")
    data_df = pd.read_sql(query, con=engine)


    if 'region' in data_df.columns and 'country' in data_df.columns and 'industry' in data_df.columns and 'company' in data_df.columns:

        df2=data_df[(data_df['region']==param2) & (data_df['country']==param3) & (data_df['industry']==param4) & (data_df['company']==param5)]
        df2['year'] = df2['year'].astype(str)

        if param1=='quarter':
            df2[['Quarter_1', 'Quarter_2', 'Quarter_3', 'Quarter_4']] = df2[['Quarter_1', 'Quarter_2', 'Quarter_3', 'Quarter_4']].fillna(0)
            fig = px.area(df2,x='year',y=['Quarter_1','Quarter_2','Quarter_3','Quarter_4'],color_discrete_sequence=px.colors.qualitative.Bold)


        if param1=='biannual':
            df2[['BiAnnual_Q1_Q2', 'BiAnnual_Q3_Q4']] = df2[['BiAnnual_Q1_Q2', 'BiAnnual_Q3_Q4']].fillna(0)
            fig = px.area(df2,x='year',y=['BiAnnual_Q1_Q2','BiAnnual_Q3_Q4'])


        if param1=='annual':
            df2['Annual'] = df2['Annual'].fillna(0)
            fig = px.area(df2,x='year',y='Annual')


    fig.update_layout(title=f'Average Salary {param1}ly in {param5}', xaxis_title='Year', yaxis_title='Average Salary', plot_bgcolor='#ffffff',legend_title_text=f'{param1}', title_x=0.5)
    return fig

@app.callback(
    Output('graph4', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value'),
     Input('industry','value'),
     Input('company', 'value'),
     Input('job-role', 'value')
    ]
)
def role_graph(param1, param2,param3,param4,param5,param6):

    if param6 is None:
        return role_default_graph()

    query = text(f"CALL generate_stats.SalaryTrend('{(param1)}', '@region={param2},@country={param3},@industry={param4},@company={param5},@role={param6},')")
    data_df = pd.read_sql(query, con=engine)
    data_df['year'] = data_df['year'].astype(str)

    if 'region' in data_df.columns and 'country' in data_df.columns and 'industry' in data_df.columns and 'company' in data_df.columns and 'job-role' in data_df.columns :
        df2=data_df[(data_df['region']==param2) & (data_df['country']==param3) & (data_df['industry']==param4) & (data_df['company']==param5) & (data_df['job-role']==param6) ]

        if param1 == 'quarter':
            df_long = pd.melt(df2, id_vars=['year'], value_vars=['Quarter_1', 'Quarter_2', 'Quarter_3', 'Quarter_4'],
                              var_name='quarter', value_name='Average Salary')

            fig = px.line(df_long, x='year', y='Average Salary', color='quarter', line_group='quarter',markers=True)
            #fig.update_traces(text=df[['Quarter_1', 'Quarter_2', 'Quarter_3', 'Quarter_4']].values.flatten(), textposition='inside', hoverinfo='y+name')

        if param1 == 'biannual':
            df_long = pd.melt(df2, id_vars=['year'], value_vars=['BiAnnual_Q1_Q2', 'BiAnnual_Q3_Q4'],
                              var_name='biannual', value_name='Average Salary')
            fig = px.line(df_long, x='year', y='Average Salary', color='biannual', line_group='biannual',markers=True)
            #fig.update_traces(text=df[['BiAnnual_Q1_Q2', 'BiAnnual_Q3_Q4']].values.flatten(), textposition='inside', hoverinfo='y+name')

        if param1 == 'annual':
            df_long = pd.melt(df2, id_vars=['year'], value_vars=['Annual'],
                              var_name='annual', value_name='value')
            fig = px.line(df_long, x='year', y='Average Salary', color='annual', line_group='annual',markers=True)
            #fig.update_traces(text=df[['Annual']].values.flatten(), textposition='inside', hoverinfo='y+name')

    fig.update_layout(title=f'Average Salary {param1}ly in {param6}',xaxis_title='Year', yaxis_title='Average Salary', plot_bgcolor='#ffffff', title_x=0.5)

    return fig

if __name__ == '__main__':

    app.run_server(debug=True, port=port)

