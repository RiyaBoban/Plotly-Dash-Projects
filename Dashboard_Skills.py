import dash
from flask import Flask
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine, text
import pandas as pd
import plotly_express as px
from dash.dash_table.Format import Group
from dash import dash_table
import plotly.graph_objects as go
import json
from collections import Counter
import itertools as it


# Create a Flask web server
server = Flask(__name__)
port = 1863

# Create a Dash web application
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Connect to the MySQL database using SQLAlchemy
engine = create_engine('mysql+pymysql://root:Matthan%40977147@localhost/generate_stats')

query = text(f"select * from generate_stats.json_daily_skills_dash")
df = pd.read_sql(query, con=engine)
df['year'] = df['year'].astype(str)
df['Top_10_skills'] = df['Top_10_skills'].apply(json.loads)
df1=df.explode('Top_10_skills').reset_index(drop=True)
df1['date'] = pd.to_datetime(df['date'])
df1['quarter1'] = (df1['date'].dt.month <= 3)
df1['quarter2'] = (df1['date'].dt.month >= 4) & (df1['date'].dt.month <= 6)
df1['quarter3'] = (df1['date'].dt.month >= 7) & (df1['date'].dt.month <= 9)
df1['quarter4'] = (df1['date'].dt.month >= 10) & (df1['date'].dt.month <= 12)
# Function to count based on specified conditions

# def count_by_conditions(dataframe, top_n=5):
#     # Group by 'Top_10_skills' and 'year' and calculate count
#     count_df = dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')
#
#     # Sort the DataFrame by 'year' and 'count'
#     count_df = count_df.sort_values(by=['year', 'count'], ascending=[True, False])
#
#     # Calculate the total count of skills in each year
#     total_count_df = count_df.groupby('year')['count'].sum().reset_index(name='TotalCount')
#
#     # Merge the counts with the totals to calculate the percentage
#     count_df = pd.merge(count_df, total_count_df, on='year')
#     count_df['Percentage'] = (count_df['count'] / count_df['TotalCount']) * 100
#
#     # Find the top 5 skills based on the percentage for each year
#     top_skills_df = count_df.groupby('year').head(top_n)
#
#     # Convert 'year' to string
#     top_skills_df['year'] = top_skills_df['year'].astype(str)
#
#     return top_skills_df





def count_by_conditions(dataframe, top_n=5):
    # Group by 'Top_10_skills' and 'year' and calculate count
    count_df = dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

    # Sort the DataFrame by 'year' and 'count'
    count_df = count_df.sort_values(by=['year', 'count'], ascending=[True, False])

    # Calculate the total count of skills in each year
    total_count_df = dataframe.groupby('year').size().reset_index(name='TotalCount')

    # Merge the counts with the totals to calculate the percentage
    count_df = pd.merge(count_df, total_count_df, on='year')
    count_df['Percentage'] = (count_df['count'] / count_df['TotalCount']) * 100

    # Find the top 5 skills based on the percentage for each year
    top_skills_df = count_df.groupby('year').head(top_n)

    # Convert 'year' to string
    top_skills_df['year'] = top_skills_df['year'].astype(str)

    return top_skills_df
df_quarter1 = count_by_conditions(df1[df1['quarter1']])

def region_default_graph():
    df1 = df.groupby(['region','year', 'Top_10_skills']).size().reset_index(name='Count')
    df1 = df1.sort_values(by=['region','year', 'Count'], ascending=[True,True, False])
    df2 = df1.groupby(['region','year']).head(5)

    default_fig=px.bar(df2,x=['Top_10_skills','year'],y='Count',color='Count',facet_col='region',text='Top_10_skills',color_continuous_scale="Purp",
                       labels={'Top_10_skills': ''},facet_col_wrap=3)
    default_fig.for_each_annotation(lambda x: x.update(text=x.text.split("=")[-1]))
    default_fig.update_layout(title='Top 5 Skills Region-wise',title_x=.5,uniformtext_minsize=12,uniformtext_mode='show',
                              font=dict(size=14),paper_bgcolor='#ffffff',plot_bgcolor='#ffffff')
    default_fig.update_traces(textangle=90, insidetextanchor='start',textfont=dict(color='black'))
    default_fig.update_xaxes(showticklabels=False)

    return default_fig

def country_default_graph():
    df1 = df.groupby(['country', 'Top_10_skills']).size().reset_index(name='Count')
    df1 = df1.sort_values(by=['country', 'Count'], ascending=[True, False])
    df2 = df1.groupby('country').head(5)

    default_fig=px.bar(df2,x='country',y='Count',color='Count',text='Top_10_skills',hover_name='Top_10_skills',color_continuous_scale="Tealgrn")
    default_fig.update_layout(title='Top 5 Skills Country-wise',title_x=.5,paper_bgcolor='#000000',font=dict(color='white'), plot_bgcolor='#000000')

    return default_fig

def industry_default_graph():
    df1 = df.groupby(['industry','year', 'Top_10_skills']).size().reset_index(name='Count')
    df1 = df1.sort_values(by=['industry','year', 'Count'], ascending=[True,True, False])
    df2 = df1.groupby(['industry','year']).head(5)

    default_fig=px.treemap(df2,path=['year','industry','Top_10_skills'],values='Count',color_discrete_sequence=px.colors.qualitative.Prism)
    default_fig.update_layout(title='Top 5 Skills Industry-wise',title_x=.5)
    return default_fig

def company_default_graph():
    df1 = df.groupby(['company', 'Top_10_skills']).size().reset_index(name='Count')
    df1 = df1.sort_values(by=['Count'], ascending=[False])
    df1 = df1.groupby('company').head(5)

    columns_to_display = ['company', 'Top_10_skills','Count']
    column_names = ['<b>Company</b>', '<b>Skills</b>','<b>Count</b>']

    default_fig = go.Figure(data=[go.Table(
        header=dict(values=list(column_names), fill_color='#56b6c4', align='left', font=dict(size=17)),
        cells=dict(values=[df1[col] for col in columns_to_display], fill_color='lavender', align='left',
                   font=dict(size=16)),
        columnwidth=[275, 125])
    ])
    default_fig.update_layout(font=dict(size=14), height=500, margin=dict(t=45), paper_bgcolor='#000000', title_x=0.5,
                              title_text='Skill Count Company-wise', title_font=dict(color='white'))
    default_fig.update_traces(cells=dict(height=30))

    return default_fig

def role_default_graph():
    df1 = df.groupby(['job-role', 'Top_10_skills']).size().reset_index(name='Count')
    df1 = df1.sort_values(by=['Count'], ascending=[False])
    df1 = df1.groupby('job-role').head(5)

    columns_to_display = ['job-role', 'Top_10_skills','Count']
    column_names = ['<b>Job Role</b>', '<b>Skills</b>','<b>Count</b>']

    default_fig = go.Figure(data=[go.Table(
        header=dict(values=list(column_names), fill_color='#56b6c4', align='left', font=dict(size=17)),
        cells=dict(values=[df1[col] for col in columns_to_display], fill_color='lavender', align='left',
                   font=dict(size=16)),
        columnwidth=[275, 125])
    ])
    default_fig.update_layout(font=dict(size=14), height=500, margin=dict(t=45), paper_bgcolor='#000000', title_x=0.5,
                              title_text='Skill Count Role-wise', title_font=dict(color='white'))
    default_fig.update_traces(cells=dict(height=30))

    return default_fig



# Define the layout of your Dash app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Skills Trend", style={'textAlign': 'center'}, className="mb-4"))
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Quarter", id='quarter-button', color="success", className="me-4"),
            dbc.Button("Biannual", id='biannual-button', color="success", className="me-4"),
            dbc.Button("Annual", id='annual-button', color="success")
        ])
    ]),
        html.Div(id='button-value', style={'display': 'none'}),

        html.Br(),

        dbc.Row([
            dbc.Col([dcc.Dropdown(id='region',options=[{'label': i, 'value': i} for i in df['region'].unique()], placeholder='Select a Region', className="mt-3")], width=6),
            dbc.Col([dcc.Dropdown(id='country', placeholder='Select a Country', className="mt-3")], width=6)
        ]),

        html.Br(),
        html.Div(children=[
            dbc.Row([
                dbc.Col([dcc.Dropdown(id='industry', placeholder='Select an Industry', className="mt-3")],
                        width={'size': 6, 'offset': 3})
            ]),

            html.Br(),

            dbc.Row([
                dbc.Col([dcc.Dropdown(id='company', placeholder='Select a Company', className="mt-3")], width=6),
                dbc.Col([dcc.Dropdown(id='job-role', placeholder='Select a Job-Role', className="mt-3")], width=6)

            ]),

            html.Br(),

            dcc.Graph(id='graph1', style={'border': '1px solid black'}, className="mt-3"),
            dcc.Graph(id='graph2', style={'border': '1px solid black'}, className="mt-3"),
            dcc.Graph(id='graph3', style={'border': '1px solid black'}, className="mt-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph4', style={'border': '1px solid black'},className="mt-3")),
        dbc.Col(dcc.Graph(id='graph5', style={'border': '1px solid black'},className="mt-3"))])

        ])
    ])



@app.callback(
    Output('country', 'options'),
    [Input('region', 'value')]
)
def update_country_options(selected_region):

    if selected_region:
        region_countries = df[df['region'] == selected_region]['country'].unique()
    else:
        region_countries = []

    return [{'label': i, 'value': i} for i in region_countries]


@app.callback(
    Output('industry', 'options'),
    [Input('country', 'value')]
)
def update_industry_options(selected_country):
    if selected_country:
        country_industry = df[df['country'] == selected_country]['industry'].unique()
    else:
        country_industry = []

    return [{'label': i, 'value': i} for i in country_industry]


@app.callback(
    Output('company', 'options'),
    [Input('industry', 'value')]
)
def update_company_options(selected_industry):
    if selected_industry:
        industry_companies = df[df['industry'] == selected_industry]['company'].unique()
    else:
        industry_companies = []

    return [{'label': i, 'value': i} for i in industry_companies]


@app.callback(
    Output('job-role', 'options'),
    [Input('company', 'value')]
)
def update_role_options(selected_company):
    if selected_company:
        company_roles = df[df['company'] == selected_company]['job-role'].unique()
    else:
        company_roles = []

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

    return None, {}, {}, {}

@app.callback(
    Output('graph1', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value')]
)
def region_graph(param1, param2):

    if param2 is None:
        return region_default_graph()

    if param2:
        query = text(f"select * from generate_stats.json_daily_skills_dash where region='{param2}' ")
        df = pd.read_sql(query, con=engine)
        df['Top_10_skills'] = df['Top_10_skills'].apply(json.loads)
        df1 = df.explode('Top_10_skills').reset_index(drop=True)



        if param1=='quarter':

            df1['date'] = pd.to_datetime(df['date'])
            df1['quarter1'] = (df1['date'].dt.month <= 3)
            df1['quarter2'] = (df1['date'].dt.month >= 4) & (df1['date'].dt.month <= 6)
            df1['quarter3'] = (df1['date'].dt.month >= 7) & (df1['date'].dt.month <= 9)
            df1['quarter4'] = (df1['date'].dt.month >= 10) & (df1['date'].dt.month <= 12)
            # Function to count based on specified conditions

            # def count_by_conditions(dataframe, top_n=5):
            #     # Group by 'Top_10_skills' and 'year' and calculate count
            #     count_df = dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')
            #
            #     # Sort the DataFrame by 'year' and 'count'
            #     count_df = count_df.sort_values(by=['year', 'count'], ascending=[True, False])
            #
            #     # Calculate the total count of skills in each year
            #     total_count_df = count_df.groupby('year')['count'].sum().reset_index(name='TotalCount')
            #
            #     # Merge the counts with the totals to calculate the percentage
            #     count_df = pd.merge(count_df, total_count_df, on='year')
            #     count_df['Percentage'] = (count_df['count'] / count_df['TotalCount']) * 100
            #
            #     # Find the top 5 skills based on the percentage for each year
            #     top_skills_df = count_df.groupby('year').head(top_n)
            #
            #     # Convert 'year' to string
            #     top_skills_df['year'] = top_skills_df['year'].astype(str)
            #
            #     return top_skills_df


            df_quarter1 = count_by_conditions(df1[df1['quarter1']])
            # df_quarter1 = df_quarter1.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_quarter1 = df_quarter1.groupby(['year']).head(5)
            df_quarter1['year'] = df_quarter1['year'].astype(str)

            df_quarter2 = count_by_conditions(df1[df1['quarter2']])
            # df_quarter2 = df_quarter2.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_quarter2 = df_quarter2.groupby(['year']).head(5)
            df_quarter2['year'] = df_quarter2['year'].astype(str)

            df_quarter3 = count_by_conditions(df1[df1['quarter3']])
            # df_quarter3 = df_quarter3.sort_values(by=['year', 'count'], ascending=[True, False])
            # df_quarter3 = df_quarter3.groupby(['year']).head(5)
            df_quarter3['year'] = df_quarter3['year'].astype(str)

            df_quarter4 = count_by_conditions(df1[df1['quarter4']])
            # df_quarter4 = df_quarter4.sort_values(by=['year', 'count'], ascending=[True, False])
            # df_quarter4 = df_quarter4.groupby(['year']).head(5)
            df_quarter4['year'] = df_quarter4['year'].astype(str)

            figure = {
                'data': [
                    {'x': df_quarter1['year'], 'y': df_quarter1['Percentage'], 'type': 'bar','marker': {'color': '#0a8e7b'},
                     'name': 'Quarter1', 'text': df_quarter1['Top_10_skills']},
                    {'x': df_quarter2['year'], 'y': df_quarter2['Percentage'], 'type': 'bar','marker': {'color': '#0cb4ac'},
                     'name': 'Quarter2', 'text': df_quarter2['Top_10_skills']},
                    {'x': df_quarter3['year'], 'y': df_quarter3['Percentage'], 'type': 'bar','marker': {'color': '#1dd6d4'},
                     'name': 'Quarter3', 'text': df_quarter3['Top_10_skills']},
                    {'x': df_quarter4['year'], 'y': df_quarter4['Percentage'], 'type': 'bar','marker': {'color': '#93e6d3'},
                     'name': 'Quarter4', 'text': df_quarter4['Top_10_skills']}
                ],
                'layout': {
                    'title': f'Quarterly Skill Count in {param2} ',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Skills Count'},
                    'barmode': 'group'  # 'group' for grouped bar chart
                }
            }
            return figure

        if param1=='biannual':
            df1['date'] = pd.to_datetime(df['date'])
            df1['first_6_months'] = (df1['date'].dt.month <= 6)
            df1['last_6_months'] = (df1['date'].dt.month >= 7)

            # Function to count based on specified conditions
            # def count_by_conditions(dataframe,top_n=5):
            #     count_df = dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')
            #
            #     # Sort the DataFrame by 'year' and 'count'
            #     count_df = count_df.sort_values(by=['year', 'count'], ascending=[True, False])
            #
            #     # Calculate the total count of skills in each year
            #     total_count_df = count_df.groupby('year')['count'].sum().reset_index(name='TotalCount')
            #
            #     # Merge the counts with the totals to calculate the percentage
            #     count_df = pd.merge(count_df, total_count_df, on='year')
            #     count_df['Percentage'] = (count_df['count'] / count_df['TotalCount']) * 100
            #
            #     # Find the top 5 skills based on the percentage for each year
            #     top_skills_df = count_df.groupby('year').head(top_n)
            #
            #     # Convert 'year' to string
            #     top_skills_df['year'] = top_skills_df['year'].astype(str)
            #
            #     return top_skills_df


            df_first_6_months = count_by_conditions(df1[df1['first_6_months']])
            # df_first_6_months = df_first_6_months.sort_values(by=['year', 'count'],ascending=[True,False])
            # df_first_6_months = df_first_6_months.groupby(['year']).head(5)
            df_first_6_months['year'] = df_first_6_months['year'].astype(str)

            df_last_6_months = count_by_conditions(df1[df1['last_6_months']])
            # df_last_6_months = df_last_6_months.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_last_6_months = df_last_6_months.groupby(['year']).head(5)
            df_last_6_months['year'] = df_last_6_months['year'].astype(str)

            figure = {
                'data': [
                    {'x': df_first_6_months['year'], 'y': df_first_6_months['Percentage'], 'type': 'bar','marker': {'color': '#0a8e7b'},
                     'name': 'First 6 Months','text':df_first_6_months['Top_10_skills']},
                    {'x': df_last_6_months['year'], 'y': df_last_6_months['Percentage'], 'type': 'bar','marker': {'color': '#0cb4ac'},
                     'name': 'Last 6 Months','text':df_last_6_months['Top_10_skills']}
                ],
                'layout': {
                    'title': f'Biannual Skill Count in {param2} ',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Skills Count'},
                    'barmode': 'group'  # 'group' for grouped bar chart
                }
            }
            return figure

        if param1 =='annual':
            # df1=df1.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')
            # df1 = df1.sort_values(by=['year', 'count'], ascending=[True, False])
            # df1 = df1.groupby(['year']).head(5)
            # df1['year'] = df1['year'].astype(str)
            df_annual = count_by_conditions(df1)
            df_annual['year'] = df_annual['year'].astype(str)

            figure = {
                'data': [
                    {'x': df_annual['year'], 'y': df_annual['Percentage'], 'type': 'bar','marker': {'color': '#0a8e7b'}, 'text': df_annual['Top_10_skills']}
                ],
                'layout': {
                    'title': f'Annual Skill Count in {param2} ',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Skills Count'},
                    'barmode': 'group'  # 'group' for grouped bar chart
                }
            }
            return figure

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

    if param3:
        query = text(f"select * from generate_stats.json_daily_skills_dash where region='{param2}' and country='{param3}'")
        df = pd.read_sql(query, con=engine)
        df['Top_10_skills'] = df['Top_10_skills'].apply(json.loads)
        df1 = df.explode('Top_10_skills').reset_index(drop=True)

        if param1=='quarter':

            df1['date'] = pd.to_datetime(df['date'])
            df1['quarter1'] = (df1['date'].dt.month <= 3)
            df1['quarter2'] = (df1['date'].dt.month >= 4) & (df1['date'].dt.month <= 6)
            df1['quarter3'] = (df1['date'].dt.month >= 7) & (df1['date'].dt.month <= 9)
            df1['quarter4'] = (df1['date'].dt.month >= 10) & (df1['date'].dt.month <= 12)
            # Function to count based on specified conditions

            # def count_by_conditions(dataframe):
            #     return dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

            df_quarter1 = count_by_conditions(df1[df1['quarter1']])
            # df_quarter1 = df_quarter1.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_quarter1 = df_quarter1.groupby(['year']).head(5)
            df_quarter1['year'] = df_quarter1['year'].astype(int)

            df_quarter2 = count_by_conditions(df1[df1['quarter2']])
            # df_quarter2 = df_quarter2.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_quarter2 = df_quarter2.groupby(['year']).head(5)
            df_quarter2['year'] = df_quarter2['year'].astype(str)

            df_quarter3 = count_by_conditions(df1[df1['quarter3']])
            # df_quarter3 = df_quarter3.sort_values(by=['year', 'count'], ascending=[True,False])
            # df_quarter3 = df_quarter3.groupby(['year']).head(5)
            df_quarter3['year'] = df_quarter3['year'].astype(int)

            df_quarter4 = count_by_conditions(df1[df1['quarter4']])
            # df_quarter4 = df_quarter4.sort_values(by=['year', 'count'], ascending=[True, False])
            # df_quarter4 = df_quarter4.groupby(['year']).head(5)
            df_quarter4['year'] = df_quarter4['year'].astype(int)

            figure = {
                'data': [
                    {'x': df_quarter1['year'], 'y': df_quarter1['Percentage'], 'type':'bar','marker': {'color':  '#125f9d'},
                     'name': 'Quarter1', 'text': df_quarter1['Top_10_skills']},
                    {'x': df_quarter2['year'], 'y': df_quarter2['Percentage'], 'type':'bar','marker': {'color':  '#5554a0'},
                     'name': 'Quarter2', 'text': df_quarter2['Top_10_skills']},
                    {'x': df_quarter3['year'], 'y': df_quarter3['Percentage'], 'type':'bar','marker': {'color': '#39a2db'},
                     'name': 'Quarter3', 'text': df_quarter3['Top_10_skills']},
                    {'x': df_quarter4['year'], 'y': df_quarter4['Percentage'], 'type':'bar','marker': {'color':'#a2dbfa'},
                     'name': 'Quarter4', 'text': df_quarter4['Top_10_skills']}
                ],
                'layout': {
                    'title': f'Quarterly Skill Count in {param3} ',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Skills Count'},
                    'barmode': 'group',


                }
            }
            return figure

        if param1=='biannual':
            df1['date'] = pd.to_datetime(df['date'])
            df1['first_6_months'] = (df1['date'].dt.month <= 6)
            df1['last_6_months'] = (df1['date'].dt.month >= 7)

            # Function to count based on specified conditions
            # def count_by_conditions(dataframe):
            #     return dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

            df_first_6_months = count_by_conditions(df1[df1['first_6_months']])
            # df_first_6_months = df_first_6_months.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_first_6_months = df_first_6_months.groupby(['year']).head(5)
            df_first_6_months['year'] = df_first_6_months['year'].astype(int)

            df_last_6_months = count_by_conditions(df1[df1['last_6_months']])
            # df_last_6_months = df_last_6_months.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_last_6_months = df_last_6_months.groupby(['year']).head(5)
            df_last_6_months['year'] = df_last_6_months['year'].astype(int)

            figure = {
                'data': [
                    {'x': df_first_6_months['year'], 'y': df_first_6_months['Percentage'], 'type': 'bar','marker': {'color':  '#125f9d'},
                     'name': 'First 6 Months','text':df_first_6_months['Top_10_skills']},
                    {'x': df_last_6_months['year'], 'y': df_last_6_months['Percentage'], 'type': 'bar','marker': {'color':  '#5554a0'},
                     'name': 'Last 6 Months','text':df_last_6_months['Top_10_skills']}
                ],
                'layout': {
                    'title': f'Biannual Skill Count in {param3} ',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Skills Count'},
                    'barmode': 'group'  # 'group' for grouped bar chart
                }
            }
            return figure

        if param1 =='annual':
            # df1=df1.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')
            # df1 = df1.sort_values(by=['year', 'count'], ascending=[True,False])
            # df1 = df1.groupby(['year']).head(5)
            # df1['year'] = df1['year'].astype(int)
            df_annual = count_by_conditions(df1)
            df_annual['year'] = df_annual['year'].astype(str)

            figure = {
                'data': [
                    {'x': df_annual['year'], 'y': df_annual['Percentage'], 'type': 'bar','color':'year','name': 'Year', 'text': df_annual['Top_10_skills']}
                ],
                'layout': {
                    'title': f'Annual Skill Count in {param3} ',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Skills Count'},
                    'barmode': 'group'  # 'group' for grouped bar chart
                }
            }
            return figure

@app.callback(
    Output('graph3', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value'),
     Input('industry', 'value')
    ]
)


def industry_graph(param1, param2, param3,param4):

    if param4 is None:
        return industry_default_graph()

    if param4:
        query = text(f"select * from generate_stats.json_daily_skills_dash where region='{param2}' and country='{param3}' and industry = '{param4}'")
        df = pd.read_sql(query, con=engine)
        df['Top_10_skills'] = df['Top_10_skills'].apply(json.loads)
        df1 = df.explode('Top_10_skills').reset_index(drop=True)

        if param1=='quarter':

            df1['date'] = pd.to_datetime(df['date'])
            df1['quarter1'] = (df1['date'].dt.month <= 3)
            df1['quarter2'] = (df1['date'].dt.month >= 4) & (df1['date'].dt.month <= 6)
            df1['quarter3'] = (df1['date'].dt.month >= 7) & (df1['date'].dt.month <= 9)
            df1['quarter4'] = (df1['date'].dt.month >= 10) & (df1['date'].dt.month <= 12)
            # Function to count based on specified conditions

            # def count_by_conditions(dataframe):
            #     return dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

            df_quarter1 = count_by_conditions(df1[df1['quarter1']])
            # df_quarter1 = df_quarter1.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_quarter1 = df_quarter1.groupby(['year']).head(5)
            df_quarter1['quarter'] = 'Quarter 1'

            df_quarter2 = count_by_conditions(df1[df1['quarter2']])
            # df_quarter2 = df_quarter2.sort_values(by=['year', 'count'],ascending=[True,False])
            # df_quarter2 = df_quarter2.groupby(['year']).head(5)
            df_quarter2['quarter'] = 'Quarter 2'

            df_quarter3 = count_by_conditions(df1[df1['quarter3']])
            # df_quarter3 = df_quarter3.sort_values(by=['year', 'count'], ascending=[True, False])
            # df_quarter3 = df_quarter3.groupby(['year']).head(5)
            df_quarter3['quarter'] = 'Quarter 3'

            df_quarter4 = count_by_conditions(df1[df1['quarter4']])
            # df_quarter4 = df_quarter4.sort_values(by=['year', 'count'], ascending=[True,False])
            # df_quarter4 = df_quarter4.groupby(['year']).head(5)
            df_quarter4['quarter']='Quarter 4'


            combined_df=pd.concat([df_quarter1,df_quarter2,df_quarter3,df_quarter4])

            fig=px.treemap(combined_df,path=['year','quarter','Top_10_skills'],values='count',color='quarter',
                           color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(title=f'Quarterly Skill Trend in {param4}', plot_bgcolor='#000000', title_x=0.5)
            return fig


        if param1=='biannual':
            df1['date'] = pd.to_datetime(df['date'])
            df1['first_6_months'] = (df1['date'].dt.month <= 6)
            df1['last_6_months'] = (df1['date'].dt.month >= 7)

            # Function to count based on specified conditions
            # def count_by_conditions(dataframe):
            #     return dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

            df_first_6_months = count_by_conditions(df1[df1['first_6_months']])
            # df_first_6_months = df_first_6_months.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_first_6_months = df_first_6_months.groupby(['year']).head(5)
            df_first_6_months['biannual'] = 'First 6 months'

            df_last_6_months = count_by_conditions(df1[df1['last_6_months']])
            # df_last_6_months = df_last_6_months.sort_values(by=['year', 'count'],ascending=[True,False])
            # df_last_6_months = df_last_6_months.groupby(['year']).head(5)
            df_last_6_months['biannual'] = 'Last 6 months'

            combined_df=pd.concat([df_first_6_months,df_last_6_months])

            fig = px.treemap(combined_df, path=['year', 'biannual', 'Top_10_skills'], values='Percentage',color='biannual',
                             color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(title=f'Biannual Skill Trend in {param4}', plot_bgcolor='#000000', title_x=0.5)
            return fig


        if param1 =='annual':
            # df1=df1.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')
            # df1 = df1.sort_values(by=['year', 'count'], ascending=[True, False])
            # df1 = df1.groupby([ 'year']).head(5)
            df_annual = count_by_conditions(df1)
            df_annual['year'] = df_annual['year'].astype(str)

            fig=px.treemap(df1, path=['year', 'Top_10_skills'], values='Percentage',color='year',color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(title=f'Annual Skill Trend in {param4}', plot_bgcolor='#000000', title_x=0.5)
            return fig

@app.callback(
    Output('graph4', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country','value'),
     Input('industry','value'),
     Input('company','value')]
)

def company_graph(param1, param2,param3,param4,param5):

    if param5 is None:
        return company_default_graph()

    if param5:
        query = text(f"select * from generate_stats.json_daily_skills_dash where region='{param2}' and country='{param3}' and industry = '{param4}' and company='{param5}'")
        df = pd.read_sql(query, con=engine)
        df['Top_10_skills'] = df['Top_10_skills'].apply(json.loads)
        df1 = df.explode('Top_10_skills').reset_index(drop=True)

        if param1=='quarter':

            df1['date'] = pd.to_datetime(df['date'])
            df1['quarter1'] = (df1['date'].dt.month <= 3)
            df1['quarter2'] = (df1['date'].dt.month >= 4) & (df1['date'].dt.month <= 6)
            df1['quarter3'] = (df1['date'].dt.month >= 7) & (df1['date'].dt.month <= 9)
            df1['quarter4'] = (df1['date'].dt.month >= 10) & (df1['date'].dt.month <= 12)
            # Function to count based on specified conditions

            # def count_by_conditions(dataframe):
            #     return dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

            df_quarter1 = count_by_conditions(df1[df1['quarter1']])
            # df_quarter1 = df_quarter1.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_quarter1 = df_quarter1.groupby(['year']).head(5)
            df_quarter1['quarter'] = 'Quarter 1'

            df_quarter2 = count_by_conditions(df1[df1['quarter2']])
            # df_quarter2 = df_quarter2.sort_values(by=['year', 'count'],ascending=[True,False])
            # df_quarter2 = df_quarter2.groupby(['year']).head(5)
            df_quarter2['quarter'] = 'Quarter 2'

            df_quarter3 = count_by_conditions(df1[df1['quarter3']])
            # df_quarter3 = df_quarter3.sort_values(by=['year', 'count'], ascending=[True, False])
            # df_quarter3 = df_quarter3.groupby(['year']).head(5)
            df_quarter3['quarter'] = 'Quarter 3'

            df_quarter4 = count_by_conditions(df1[df1['quarter4']])
            # df_quarter4 = df_quarter4.sort_values(by=['year', 'count'], ascending=[True,False])
            # df_quarter4 = df_quarter4.groupby(['year']).head(5)
            df_quarter4['quarter']='Quarter 4'


            combined_df=pd.concat([df_quarter1,df_quarter2,df_quarter3,df_quarter4])

            fig=px.sunburst(combined_df,path=['year','quarter','Top_10_skills'],values='Percentage',color='quarter',
                            color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(title=f'Quarterly Skill Trend in {param5}', plot_bgcolor='#000000', title_x=0.5)
            return fig

        if param1=='biannual':
            df1['date'] = pd.to_datetime(df['date'])
            df1['first_6_months'] = (df1['date'].dt.month <= 6)
            df1['last_6_months'] = (df1['date'].dt.month >= 7)

            # Function to count based on specified conditions
            # def count_by_conditions(dataframe):
            #     return dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

            df_first_6_months = count_by_conditions(df1[df1['first_6_months']])
            # df_first_6_months = df_first_6_months.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_first_6_months = df_first_6_months.groupby(['year']).head(5)
            df_first_6_months['biannual'] = 'First 6 months'

            df_last_6_months = count_by_conditions(df1[df1['last_6_months']])
            # df_last_6_months = df_last_6_months.sort_values(by=['year', 'count'],ascending=[True,False])
            # df_last_6_months = df_last_6_months.groupby(['year']).head(5)
            df_last_6_months['biannual'] = 'Last 6 months'

            combined_df=pd.concat([df_first_6_months,df_last_6_months])

            fig = px.sunburst(combined_df, path=['year', 'biannual', 'Top_10_skills'], values='Percentage',color='biannual',color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(title=f'Biannual Skill Trend in {param5}', plot_bgcolor='#000000', title_x=0.5)
            return fig


        if param1 =='annual':
            # df1=df1.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')
            # df1 = df1.sort_values(by=['year', 'count'], ascending=[True, False])
            # df1 = df1.groupby([ 'year']).head(5)
            df_annual = count_by_conditions(df1)
            df_annual['year'] = df_annual['year'].astype(str)

            fig=px.sunburst(df1, path=['year', 'Top_10_skills'], values='Percentage',color='year',color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(title=f'Annual Skill Trend in {param5}', plot_bgcolor='#000000', title_x=0.5)
            return fig


@app.callback(
    Output('graph5', 'figure'),
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country','value'),
     Input('industry','value'),
     Input('company','value'),
     Input('job-role','value')]
)

def role_graph(param1, param2,param3,param4,param5,param6):

    if param6 is None:
        return role_default_graph()

    if param6:
        query = text(f"select * from generate_stats.json_daily_skills_dash where region='{param2}' and country='{param3}' and industry = '{param4}' and company='{param5}' and `job-role`='{param6}'")
        df = pd.read_sql(query, con=engine)
        df['Top_10_skills'] = df['Top_10_skills'].apply(json.loads)
        df1 = df.explode('Top_10_skills').reset_index(drop=True)

        if param1=='quarter':

            df1['date'] = pd.to_datetime(df['date'])
            df1['quarter1'] = (df1['date'].dt.month <= 3)
            df1['quarter2'] = (df1['date'].dt.month >= 4) & (df1['date'].dt.month <= 6)
            df1['quarter3'] = (df1['date'].dt.month >= 7) & (df1['date'].dt.month <= 9)
            df1['quarter4'] = (df1['date'].dt.month >= 10) & (df1['date'].dt.month <= 12)
            # Function to count based on specified conditions

            # def count_by_conditions(dataframe):
            #     return dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

            df_quarter1 = count_by_conditions(df1[df1['quarter1']])
            # df_quarter1 = df_quarter1.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_quarter1 = df_quarter1.groupby(['year']).head(5)
            df_quarter1['quarter'] = 'Quarter 1'

            df_quarter2 = count_by_conditions(df1[df1['quarter2']])
            # df_quarter2 = df_quarter2.sort_values(by=['year', 'count'],ascending=[True,False])
            # df_quarter2 = df_quarter2.groupby(['year']).head(5)
            df_quarter2['quarter'] = 'Quarter 2'

            df_quarter3 = count_by_conditions(df1[df1['quarter3']])
            # df_quarter3 = df_quarter3.sort_values(by=['year', 'count'], ascending=[True, False])
            # df_quarter3 = df_quarter3.groupby(['year']).head(5)
            df_quarter3['quarter'] = 'Quarter 3'

            df_quarter4 = count_by_conditions(df1[df1['quarter4']])
            # df_quarter4 = df_quarter4.sort_values(by=['year', 'count'], ascending=[True,False])
            # df_quarter4 = df_quarter4.groupby(['year']).head(5)
            df_quarter4['quarter']='Quarter 4'


            combined_df=pd.concat([df_quarter1,df_quarter2,df_quarter3,df_quarter4])

            fig=px.sunburst(combined_df,path=['year','quarter','Top_10_skills'],values='Percentage',color='quarter',
                            color_discrete_sequence=px.colors.qualitative.Vivid)
            fig.update_layout(title=f'Quarterly Skill Trend in {param6}', plot_bgcolor='#000000', title_x=0.5)
            return fig

        if param1=='biannual':
            df1['date'] = pd.to_datetime(df['date'])
            df1['first_6_months'] = (df1['date'].dt.month <= 6)
            df1['last_6_months'] = (df1['date'].dt.month >= 7)

            # Function to count based on specified conditions
            # def count_by_conditions(dataframe):
            #     return dataframe.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')

            df_first_6_months = count_by_conditions(df1[df1['first_6_months']])
            # df_first_6_months = df_first_6_months.sort_values(by=['year', 'count'],ascending=[True, False])
            # df_first_6_months = df_first_6_months.groupby(['year']).head(5)
            df_first_6_months['biannual'] = 'First 6 months'

            df_last_6_months = count_by_conditions(df1[df1['last_6_months']])
            # df_last_6_months = df_last_6_months.sort_values(by=['year', 'count'],ascending=[True,False])
            # df_last_6_months = df_last_6_months.groupby(['year']).head(5)
            df_last_6_months['biannual'] = 'Last 6 months'

            combined_df=pd.concat([df_first_6_months,df_last_6_months])

            fig = px.sunburst(combined_df, path=['year', 'biannual', 'Top_10_skills'], values='Percentage',color='biannual',
                              color_discrete_sequence=px.colors.qualitative.Vivid)
            fig.update_layout(title=f'Biannual Skill Trend in {param6}', plot_bgcolor='#000000', title_x=0.5)
            return fig


        if param1 =='annual':
            # df1=df1.groupby(['Top_10_skills', 'year']).size().reset_index(name='count')
            # df1 = df1.sort_values(by=['year', 'count'], ascending=[True, False])
            # df1 = df1.groupby([ 'year']).head(5)
            df_annual = count_by_conditions(df1)
            df_annual['year'] = df_annual['year'].astype(str)

            fig=px.sunburst(df1, path=['year', 'Top_10_skills'], values='Percentage',color='year',color_discrete_sequence=px.colors.qualitative.Vivid)
            fig.update_layout(title=f'Annual Skill Trend in {param6}', plot_bgcolor='#000000', title_x=0.5)
            return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=port)
