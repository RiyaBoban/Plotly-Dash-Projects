import json
import dash
from flask import Flask
from dash import Dash, dcc, html, no_update
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine, text
import pandas as pd
import plotly_express as px
from dash.dash_table.Format import Group
from dash import dash_table
import plotly.graph_objects as go

DataTable = dash_table.DataTable

# Create a Flask web server
server = Flask(__name__)
port = 1864

# Create a Dash web application
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Connect to the MySQL database using SQLAlchemy
engine = create_engine('mysql+pymysql://root:Matthan%40977147@localhost/generate_stats')

query = text(f"select * from generate_stats.skills_dash_csv")
df = pd.read_sql(query, con=engine)
df['Year'] = df['Year'].astype(str)
# df['Top_10_skills'] = df['Top_10_skills'].apply(json.loads)
# df=df.explode('Top_10_skills').reset_index(drop=True)

def biannual_dataframe(dataframe):

        #dataframe['Date'] = pd.to_datetime(dataframe['Date'])
        dataframe['Date'] = pd.to_datetime(dataframe['Date'], format="%d-%m-%Y")
        dataframe['first_6_months'] = (dataframe['Date'].dt.month <= 6)
        dataframe['last_6_months'] = (dataframe['Date'].dt.month >= 7)


        def count_by_conditions(dataframe):
            return dataframe.groupby(['Skills', 'Year']).size().reset_index(name='count')


        df_first_6_months = count_by_conditions(dataframe[dataframe['first_6_months']])
        df_first_6_months = df_first_6_months.sort_values(by=['Year', 'count'], ascending=[True, False])
        df_first_6_months = df_first_6_months.groupby(['Year']).head(5)
        df_first_6_months['Year'] = df_first_6_months['Year'].astype(int)
        df_first_6_months['biannual'] = 'First 6 months'

        df_last_6_months = count_by_conditions(dataframe[dataframe['last_6_months']])
        df_last_6_months = df_last_6_months.sort_values(by=['Year', 'count'], ascending=[True, False])
        df_last_6_months = df_last_6_months.groupby(['Year']).head(5)
        df_last_6_months['Year'] = df_last_6_months['Year'].astype(int)
        df_last_6_months['biannual'] = 'Last 6 months'
        combined_df = pd.concat([df_first_6_months, df_last_6_months])
        return combined_df
#df1=biannual_dataframe(df)
def annual_dataframe(dataframe):
        df_annual = dataframe.groupby(['Skills', 'Year']).size().reset_index(name='count')
        df_annual = df_annual.sort_values(by=['Year', 'count'], ascending=[True, False])
        df_annual = df_annual.groupby(['Year']).head(5)
        return df_annual

def biannual_percentage(dataframe):
    top_5df=biannual_dataframe(dataframe)
    total_count_df = dataframe.groupby('Year').size().reset_index(name='TotalCount')
    top_5df['Year'] = top_5df['Year'].astype(str)
    top_5df = pd.merge(top_5df, total_count_df, on='Year', how='left')
    top_5df['Percentage'] = (top_5df['count'] / top_5df['TotalCount']) * 100
    return top_5df

def annual_percentage(dataframe):
    top_5df = annual_dataframe(dataframe)
    total_count_df = dataframe.groupby('Year').size().reset_index(name='TotalCount')
    top_5df['Year'] = top_5df['Year'].astype(str)
    top_5df = pd.merge(top_5df, total_count_df, on='Year', how='left')
    top_5df['Percentage'] = (top_5df['count'] / top_5df['TotalCount']) * 100
    return top_5df

# Define the layout of your Dash app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Skills Trend", style={'textAlign': 'center'}, className="mb-4"))
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Biannual", id='biannual-button', color="primary", className="me-4"),
            dbc.Button("Annual", id='annual-button', color="primary", className="me-4"),
            # dbc.Button("Biannual_Percentage", id='percentage-biannual-button', color="success", className="me-4"),
            # dbc.Button("Annual_Percentage", id='percentage-annual-button', color="success", className="me-4"),
        ]),
        html.Div(id='button-value', style={'display': 'none'}),

        html.Br(),

        dbc.Row([
            dbc.Col([dcc.Dropdown(id='region',
                                  options=[{'label': i, 'value': i} for i in df['Region'].unique()],
                                  placeholder='Select a Region', className="mt-3")], width=6),

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
            dbc.Button('Go Back', id='back', size='sm', active=True, color='primary', style={'display': 'none'}),
                dcc.Graph(id='graph1', style={'border': '1px solid black', 'height': '750px', 'display': 'none'}, className="mt-3"),
                dcc.Graph(id='graph2', style={'border': '1px solid black','height': '750px','display': 'none'}, className="mt-3"),
                dcc.Graph(id='graph3', style={'border': '1px solid black','height': '750px','display': 'none'},className="mt-3"),

                dcc.Graph(id='graph4', style={'border': '1px solid black','height': '750px','display': 'none'}, className="mt-3"),
                dcc.Graph(id='graph5', style={'border': '1px solid black','height': '750px','display': 'none'}, className="mt-3"),
            ])

        ])
    ])



@app.callback(
    Output('country', 'options'),
    [Input('region', 'value')]
)
def update_country_options(selected_region):
    if selected_region:
        region_countries = df[df['Region'] == selected_region]['Country'].unique()
    else:
        region_countries = []

    return  [{'label': i, 'value': i} for i in region_countries]


@app.callback(
    Output('industry', 'options'),
    [Input('country', 'value')]
)
def update_industry_options(selected_country):
    if selected_country:
        country_industry = df[df['Country'] == selected_country]['Industry'].unique()
    else:
        country_industry = []
    return [{'label': i, 'value': i} for i in country_industry]


@app.callback(
    Output('company', 'options'),
    [Input('industry', 'value')]
)
def update_company_options(selected_industry):
    if selected_industry:
        industry_companies = df[df['Industry'] == selected_industry]['Company'].unique()
    else:
        industry_companies = []
    return [{'label': i, 'value': i} for i in industry_companies]


@app.callback(
    Output('job-role', 'options'),
    [Input('company', 'value'),
     Input('country', 'value'),
     Input('industry', 'value')]
)
def update_role_options(selected_company, selected_country, selected_industry):
    if selected_company and selected_industry:
        company_roles = df[(df['Company'] == selected_company) & (df['Industry'] == selected_industry)]['Job_role'].unique()
        return [{'label': i, 'value': i} for i in company_roles]
    elif selected_country :
        country_roles = df[(df['Country'] == selected_country)]['Job_role'].unique()
        return [{'label': i, 'value': i} for i in country_roles]

    return []


@app.callback(
    [Output('button-value', 'children'),
     Output('biannual-button', 'style'),
     Output('annual-button', 'style'),
     # Output('percentage-biannual-button','style'),
     # Output('percentage-annual-button','style')
     ],
    [Input('biannual-button', 'n_clicks'),
     Input('annual-button', 'n_clicks'),
     # Input('percentage-biannual-button','n_clicks'),
     # Input('percentage-annual-button','n_clicks')
    ]
)
def update_button_value(n_clicks_biannual, n_clicks_annual):
                        # ,n_clicks_biannual_percentage,n_clicks_annual_percentage):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == 'biannual-button':
        return 'biannual', {}, {}
    elif trigger_id == 'annual-button':
        return 'annual', {}, {}
    # elif trigger_id =='percentage-biannual-button':
    #     return 'percentage1',{},{},{}, {}
    # elif trigger_id =='percentage-annual-button':
    #     return 'percentage2',{},{},{}, {}
    return None, {}, {}

@app.callback(
    [Output('graph1', 'figure'),
    Output('graph1', 'style')],
    [Input('button-value', 'children'),
     Input('region', 'value')
     ]
)
def region_graph(param1, param2):


    if not param2:
        return no_update, {'display': 'none'}

    if param2:
        query = text(f"select * from generate_stats.skills_dash_csv where Region='{param2}'")
        df1 = pd.read_sql(query, con=engine)
        df1['Year'] = df1['Year'].astype(str)
        # df1['Top_10_skills'] = df1['Top_10_skills'].apply(json.loads)
        # df1 = df.explode('Top_10_skills').reset_index(drop=True)

        if param1 == 'biannual':

            biannual_df=biannual_percentage(df1)
            biannual_df['Percentage'] = biannual_df['Percentage'].astype(float)
            fig=px.treemap(biannual_df, path=['Year', 'biannual', 'Skills'],color='Skills',values='Percentage',
                           color_discrete_sequence=px.colors.qualitative.Alphabet_r)
            fig.update_layout(title=f'Biannual Skill Trend in {param2}', font=dict(size=17),
                              margin = dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5)
            # fig.update_traces(
            #     hovertemplate='<b>%{label}</b><br>Percentage: %{percent:%}'
            # )
            fig.update_traces(
                texttemplate='%{label}<br>%{value:.2f}%',  # Display the label (skill name)
                textposition='middle center')
               #hovertemplate='<b>%{label}</b><br>$%{value:.2f}')
            return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

        elif param1 == 'annual':
            annual_df=annual_percentage(df1)

            fig = px.treemap(annual_df, path=['Year', 'Skills'], color='Skills',values='Percentage',
                             color_discrete_sequence=px.colors.qualitative.Alphabet_r)
            fig.update_layout(title=f'Annual Skill Trend in {param2}', font=dict(
                        size=17), margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5,xaxis=dict(tickangle=-45))
            fig.update_traces(
                texttemplate='%{label}<br>%{value:.2f}%',  # Display the label (skill name)
                textposition='middle center' )

            return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

        # elif param1== 'percentage1':
        #     percentage_biannual_df=biannual_percentage(df1)
        #     fig = px.bar(percentage_biannual_df,x='year',y='Percentage',color='biannual',text='Top_10_skills',labels={'biannual': ''})
        #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
        #     return fig,{'border': '1px solid black', 'height': '750px', 'display': 'block'}
        #
        # elif param1== 'percentage2':
        #
        #     percentage_annual_df = annual_percentage(df1)
        #     fig = px.bar(percentage_annual_df,x='year',y='Percentage',color='year',text='Top_10_skills',labels={'year': ''})
        #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
        #     return fig,{'border': '1px solid black', 'height': '750px', 'display': 'block'}

@app.callback(
    [Output('graph2', 'figure'),
    Output('graph2', 'style')],
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value')
     ]
)
def country_graph(param1, param2, param3):

    if not param3:
        return no_update, {'display': 'none'}

    if param3:
        query = text(f"select * from generate_stats.skills_dash_csv where region='{param2}' and country ='{param3}'")
        df2 = pd.read_sql(query, con=engine)
        df2['Year'] = df2['Year'].astype(str)
        # df2['Top_10_skills'] = df2['Top_10_skills'].apply(json.loads)
        # df2 = df2.explode('Top_10_skills').reset_index(drop=True)

        if param1 == 'biannual':
            biannual_df=biannual_percentage(df2)

            fig = px.treemap(biannual_df, path=['Year', 'biannual', 'Skills'], color='Skills',values='Percentage',
                             color_discrete_sequence=px.colors.qualitative.Alphabet_r)
            fig.update_layout(title=f'Biannual Skill Trend in {param3}', font=dict(size=17),
                              margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5)
            fig.update_traces(
                texttemplate='%{label}<br>%{value:.2f}%',  # Display the label (skill name)
                textposition='middle center')
            return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}


        elif param1 == 'annual':

            annual_df=annual_percentage(df2)

            fig = px.treemap(annual_df, path=['Year', 'Skills'], color='Skills',values='Percentage',
                             color_discrete_sequence=px.colors.qualitative.Alphabet_r)
            fig.update_layout(title=f'Annual Skill Trend in {param3}', font=dict(
                size=17), margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5,
                              xaxis=dict(tickangle=-45))
            fig.update_traces(
                texttemplate='%{label}<br>%{value:.2f}%',  # Display the label (skill name)
                textposition='middle center')

            return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

        # elif param1 == 'percentage1':
        #     percentage_biannual_df = biannual_percentage(df2)
        #     fig = px.bar(percentage_biannual_df, x='year', y='Percentage', color='biannual', text='Top_10_skills',
        #                  labels={'biannual': ''})
        #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
        #     return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}
        #
        # elif param1 == 'percentage2':
        #
        #     percentage_annual_df = annual_percentage(df2)
        #     fig = px.bar(percentage_annual_df, x='year', y='Percentage', color='year', text='Top_10_skills', labels={'year': ''})
        #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
        #     return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

@app.callback(
    [Output('graph3', 'figure'),
    Output('graph3', 'style')],
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value'),
     Input('industry', 'value')]
)
def industry_graph(param1, param2, param3, param4):

    if not param4:
        return no_update, {'display': 'none'}

    if param4:
        query = text(f"select * from generate_stats.skills_dash_csv where region='{param2}' and country ='{param3}' and industry ='{param4}'")
        df3 = pd.read_sql(query, con=engine)
        df3['Year'] = df3['Year'].astype(str)
        # df3['Top_10_skills'] = df3['Top_10_skills'].apply(json.loads)
        # df3 = df3.explode('Top_10_skills').reset_index(drop=True)

        if param1 == 'biannual':

            biannual_df = biannual_percentage(df3)

            fig = px.treemap(biannual_df, path=['Year', 'biannual', 'Skills'], color='Skills',values='Percentage',
                             color_discrete_sequence=px.colors.qualitative.Alphabet_r)
            fig.update_layout(title=f'Biannual Skill Trend in {param4}', font=dict(size=17),
                              margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5)
            fig.update_traces(
                texttemplate='%{label}<br>%{value:.2f}%',  # Display the label (skill name)
                textposition='middle center')
            return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

        elif param1 == 'annual':
            annual_df = annual_percentage(df3)

            fig = px.treemap(annual_df, path=['Year', 'Skills'], color='Skills',values='Percentage',
                             color_discrete_sequence=px.colors.qualitative.Alphabet_r)
            fig.update_layout(title=f'Annual Skill Trend in {param4}', font=dict(
                size=17), margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5,
                              xaxis=dict(tickangle=-45))
            fig.update_traces(
                texttemplate='%{label}<br>%{value:.2f}%',  # Display the label (skill name)
                textposition='middle center')
            return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

        # elif param1 == 'percentage1':
        #     percentage_biannual_df = biannual_percentage(df3)
        #     fig = px.bar(percentage_biannual_df, x='year', y='Percentage', color='biannual',
        #                  text='Top_10_skills',
        #                  labels={'biannual': ''})
        #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
        #     return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}
        #
        # elif param1 == 'percentage2':
        #
        #     percentage_annual_df = annual_percentage(df3)
        #     fig = px.bar(percentage_annual_df, x='year', y='Percentage', color='year', text='Top_10_skills',
        #                  labels={'year': ''})
        #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
        #     return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}


@app.callback(
    [Output('graph4', 'figure'),
    Output('graph4', 'style')],
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value'),
     Input('industry', 'value'),
     Input('company', 'value')]
)
def company_graph(param1, param2, param3, param4, param5):

    if not param5:
        return no_update, {'display': 'none'}

    if param5:
        query = text(
            f"select * from generate_stats.skills_dash_csv where region='{param2}' and country ='{param3}' and industry ='{param4}' and company ='{param5}'")
        df4 = pd.read_sql(query, con=engine)
        df4['Year'] = df4['Year'].astype(str)
        # df4['Top_10_skills'] = df4['Top_10_skills'].apply(json.loads)
        # df4 = df4.explode('Top_10_skills').reset_index(drop=True)

        if param1 == 'biannual':

            biannual_df = biannual_percentage(df4)

            fig = px.sunburst(biannual_df, path=['Year', 'biannual', 'Skills'], color='Skills',values='Percentage',
                             color_discrete_sequence=px.colors.qualitative.Vivid)
            fig.update_traces(texttemplate='%{label}<br>%{percentParent:.2%}')

            fig.update_layout(title=f'Biannual Skill Trend in {param5}', font=dict(size=17),
                              margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5)
            return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

        elif param1 == 'annual':
            annual_df = annual_percentage(df4)

            fig = px.sunburst(annual_df, path=['Year', 'Skills'], color='Skills',values='Percentage',
                             color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_traces(texttemplate='%{label}<br>%{percentParent:.2%}')
            fig.update_layout(title=f'Annual Skill Trend in {param5}', font=dict(
                size=17), margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5,
                              xaxis=dict(tickangle=-45))
            return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

        # elif param1 == 'percentage1':
        #
        #     percentage_biannual_df = biannual_percentage(df4)
        #     fig = px.bar(percentage_biannual_df, x='year', y='Percentage', color='biannual', text='Top_10_skills',
        #                  labels={'biannual': ''})
        #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
        #     return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}
        #
        # elif param1 == 'percentage2':
        #
        #     percentage_annual_df = annual_percentage(df4)
        #     fig = px.bar(percentage_annual_df, x='year', y='Percentage', color='year', text='Top_10_skills', labels={'year': ''})
        #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
        #     return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

@app.callback(
    [Output('graph5', 'figure'),
    Output('graph5', 'style')],
    [Input('button-value', 'children'),
     Input('region', 'value'),
     Input('country', 'value'),
     Input('industry', 'value'),
     Input('company', 'value'),
     Input('job-role', 'value')]
)
def role_graph(param1, param2, param3, param4, param5, param6):

    if not param6:
        return no_update, {'display': 'none'}

    if  param2 and param3 and param4 and param5 and param6:

        query = text(
            f"select * from generate_stats.skills_dash_csv where region='{param2}' and country ='{param3}' and industry ='{param4}' and company ='{param5}'and `job_role`='{param6}'")

    elif param2 and param3  and param6 :

        query = text(f"select * from generate_stats.skills_dash_csv where region='{param2}' and country ='{param3}' and `job_role`='{param6}'")


    df5 = pd.read_sql(query, con=engine)
    df5['Year'] = df5['Year'].astype(str)
    # df5['Top_10_skills'] = df5['Top_10_skills'].apply(json.loads)
    # df5 = df5.explode('Top_10_skills').reset_index(drop=True)

    if param1 == 'biannual':

        biannual_df = biannual_percentage(df5)

        fig = px.sunburst(biannual_df, path=['Year', 'biannual', 'Skills'], color='Skills',values='Percentage',
                          color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_traces(texttemplate='%{label}<br>%{percentParent:.2%}')
        fig.update_layout(title=f'Biannual Skill Trend in {param6}', font=dict(size=17),
                          margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5)
        return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

    elif param1 == 'annual':

        annual_df = annual_percentage(df5)

        fig = px.sunburst(annual_df, path=['Year', 'Skills'], color='Skills',values='Percentage',
                          color_discrete_sequence=px.colors.qualitative.Prism)
        #fig.update_traces(texttemplate='%{label}<br>%{percentParent:.2%}')
        fig.update_layout(title=f'Annual Skill Trend in {param6}', font=dict(
            size=17), margin=dict(t=45, l=20, r=20, b=20), plot_bgcolor='#000000', title_x=0.5,
                          xaxis=dict(tickangle=-45))
        return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}

    # elif param1 == 'percentage1':
    #     percentage_biannual_df = biannual_percentage(df5)
    #     fig = px.bar(percentage_biannual_df, x='year', y='Percentage', color='biannual', text='Top_10_skills',
    #                  labels={'biannual': ''})
    #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
    #     return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}
    #
    # elif param1 == 'percentage2':
    #
    #     percentage_annual_df = annual_percentage(df5)
    #     fig = px.bar(percentage_annual_df, x='year', y='Percentage', color='year', text='Top_10_skills', labels={'year': ''})
    #     fig.update_traces(texttemplate='%{y:.2f}% | %{text}', textposition='inside',textfont=dict(size=16))
    #     return fig, {'border': '1px solid black', 'height': '750px', 'display': 'block'}



if __name__ == '__main__':
    app.run_server(debug=True, port=port)