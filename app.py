from dash import Dash, dcc, html, ALL, dash_table, ctx
# import dash_auth
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import warnings
import data_tracking as dat
import dqi_tracking as dqi
import query_tracking as qtk
# import auth as auth
# from flask_caching import Cache
# import gunicorn

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

# PASSWORDS = auth.VALID_USERNAME_PASSWORD_PAIRS
feather = dat.feather

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "32rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "scroll",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-top": "2rem",
    "margin-left": "33rem",
    "margin-right": "1rem",
    # "padding": "2rem 1rem",
}

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, 'https://codepen.io/chriddyp/pen/bWLwgP.css'], suppress_callback_exceptions=True)
# auth = dash_auth.BasicAuth(
#     app,
#     PASSWORDS
# )
# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache-directory'
# })

# TIMEOUT = 200

app.layout = html.Div(className='row', children=[
    # html.H1('F-Data Tracking', style={'textAlign': 'center',}),
    dcc.Location(id='url'),
    dbc.NavbarSimple(children=[
            dbc.DropdownMenu(
            children=[
                # dbc.DropdownMenuItem(" Data Source Comparison ", header=True),
                dbc.DropdownMenuItem("Published Data (FA.gov)", href="/faid",external_link=True, active="exact"),
                dbc.DropdownMenuItem(" Internal Data (CGFS Extracts) ", href="/fadr",external_link=True, active="exact"),
                dbc.DropdownMenuItem(" Combined (Beta) ", href="/combined",external_link=True, active="exact"),
            ],
            nav=True,
            in_navbar=True,
            label="Data Source Comparison",
        ),
            dbc.NavItem(dbc.NavLink("Data Quality Improvements", href="/dqi",external_link=True, active="exact")),
            dbc.NavItem(dbc.NavLink("QUERY Tool (Beta)", href="/query",external_link=True, active="exact")),
            
        ],
        brand='F-Data Tracking',
        brand_href="/",
        color='primary',
        dark=True,
        fluid=True,
        sticky='top',
        ),
    html.Div(id='tabs-content-dropdowns', style={"margin-bottom": "35px",'display': 'inline-block'}),
    dcc.Loading(
            color="#2C3E50",
            id="loading-1",
            type="default",
            children=html.Div(id='tabs-content-graphs', style={"margin-bottom": "35px",'display': 'inline-block'}), style={"margin-bottom": "35px",'display': 'inline-block', 'width':'99%'}),
    html.Div(children=[html.P('''\n\n\nPublished FA.gov data is current as of the website on 5 May 2023. Internal data is current through FY23 Q1.''')], style={"margin-top": "25px"})
], style=CONTENT_STYLE)#style={"border":"10px white solid",'display': 'inline-block'})

server = app.server
                                                                                          
@app.callback(Output('tabs-content-dropdowns','children'),
              Input('url','pathname'))
              # Input('tabs-faid-fadr-tracking','value'))

def render_tabs(tab):
    if tab == '/':
        return html.Div(children=[
            html.Div(children=[
                        html.H3('F-Data Tracking:', style={'margin-top':'25px'}),
                        html.Div(children=[
                            # html.Img(src='https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Seal_of_the_United_States_Department_of_State.svg/2048px-Seal_of_the_United_States_Department_of_State.svg.png',
                            #          style={'margin-top':'25px','height':'90%','width':'90%'}),
                            html.Div(children=[
                                    html.H5('Links to Additional Resources:'),
    
                                ], style={"margin-top":"35px",'text-align':'center'}),
                            html.Div(
                                    html.A("ForeignAssistance.gov", href="https://foreignassistance.gov/"),
                                ),
                            html.Div(
                                html.A("USAID FA.gov API Site", href="https://data.usaid.gov/Administration-and-Oversight/ForeignAssistance-gov-Complete/azij-hu6e")
                            ),
                ])
            ],style=SIDEBAR_STYLE),
            html.Div(children=[
                html.H5('Welcome to the F-Data Tracker'),
                html.Div(children=[
                        html.P('''The purpose of this tracking app is to provide members of the F-Data team the ability to visualize, understand,
                                  and ask questions of quarterly Department of State foreign assistance data.'''),
                        html.P('''\n\nThe first option on the task bar is a dropdown showing spending patterns at the bureau, year, and location level
                                  for both published and unpuplished data. Users can select either all obligated data or all disbursement data to see both what
                                  has been committed and what has already been spent. Users can also group spending for internal data by the year
                                  in which the transaction occurred or the year when the award was first obligated.'''),
                        html.P('''\n\nThe Third dropdown option, "Combined (Beta), allows users to create simple bar charts to directly compare between published and 
                                  internal data. This functionality is still in development, so please report any found bugs.'''),
                        html.P('''\n\nThe Data Quality Improvement tab is designed to inform bureau outreach and measure 
                                  progress in aligning foreign assistance data entry with US goals of accuracy and transparency.'''),
                        html.P('''\n\nThe final tab allows users to query published and internal data in order to respond to internal or
                                  external data calls. Data is filterable by bureau, year, sector, and location. Multiple values are selectable 
                                  for each field.'''),
                        html.P('''\n\nFor access to the full foreign assistance dataset, as well as documentation of what all columns mean and additional
                                  visualization tools, visit https://foreignassistance.gov/''')
                    ], style={'margin-top':'25px','font-size':'14px'}),

                # html.P('''\n[LARGE IMAGE WILL GO HERE]'''),
            ])
        ])
    elif tab == '/faid':
        
        df = pd.concat([pd.read_feather(fr"{feather}/FAID_full_1"),pd.read_feather(fr"{feather}/FAID_full_2")]).reset_index(drop=True)
        df = df.loc[df['Managing Agency']=='Department of State']

        df_burs = ['All'] + sorted(df['bureau'].astype(str).unique().tolist())
        df_yrs = ['All'] + sorted(df['Fiscal Year'].astype(str).unique().tolist())

        return html.Div(children=[
            html.Div(children=[
                html.H3('Filters:', style={"margin-top":"25px"}),
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5('Bureau:'),
                                dcc.Dropdown(df_burs, 'All', id={'name':'bureau_dash',
                                                                  'type':'filter-dropdown',
                                                                  'index':0}),
                                html.H5('Spending Type:', style={"margin-top": "5px"}),
                                dcc.Dropdown(['Obligations','Disbursements'], 'Obligations', id={'name':'spnd_type_dash',
                                                                                                   'type':'filter-dropdown',
                                                                                                   'index':1}),
                                html.H5('Year:', style={"margin-top": "5px"}),
                                dcc.Dropdown(df_yrs, 'All', id={'name':'year_dash',
                                                                 'type':'filter-dropdown',
                                                                 'index':2}),
                                html.H5('Year Calculation:', style={"margin-top": "5px"}),
                                dcc.Dropdown(['Transaction Fiscal Year',
                                              'Award Start Year'], 'Transaction Fiscal Year', id={'name':'year_type_dash',
                                                                                                  'type':'filter-dropdown',
                                                                                                  'index':3}),
                                dbc.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"margin-top": "5px"}),
                            ]
                        ),
                    ],
                    style={"margin-top":"5px"},
                ),
                ], style=SIDEBAR_STYLE
            ),
            html.Div(children=[
                html.H4('Data Comparison Introduction:', style={"margin-top":"25px"}
                        ),
                html.P('''The purpose of the data comparison dropdown is to provide members of the F-Data team the ability to visualize, understand,
                          and ask questions of quarterly Department of State foreign assistance data.'''),
                html.P('''\n\nThe first two options of this dropdown show spending patterns at the bureau, year, and location level
                          for both published and unpuplished data. Users can select either all obligated data or all disbursement data to see both what
                          has been committed and what has already been spent. Users can also group spending for internal data by the year
                          in which the transaction occurred or the year when the award was first obligated.'''),
                html.P('''\n\nThe third dropdown option, "Combined (Beta), allows users to create simple bar charts to directly compare between published and 
                          internal data. This functionality is still in development, so please report any found bugs.'''),
                html.P('''\n\nFor access to the full foreign assistance dataset, as well as documentation of what all columns mean and additional
                          visualization tools, visit https://foreignassistance.gov/''')]
                        ,) #style={'width': '64%', 'display':'inline-block', "margin-left": "15px"})
        ])
    elif tab == '/fadr':
        
        df = pd.concat([pd.read_feather(fr"{feather}/FADR_full_1"),pd.read_feather(fr"{feather}/FADR_full_2")]).reset_index(drop=True)

        df_burs = ['All'] + sorted(df['bureau'].astype(str).unique().tolist())
        df_yrs = ['All'] + sorted(df['year'].astype(str).unique().tolist())

        return html.Div(children=[
            html.Div(children=[
                html.H3('Filters:', style={"margin-top":"25px"}),
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5('Bureau:'),
                                dcc.Dropdown(df_burs, 'All', id={'name':'bureau_dash',
                                                                  'type':'filter-dropdown',
                                                                  'index':0}),
                                html.H5('Spending Type:', style={"margin-top": "5px"}),
                                dcc.Dropdown(['Obligations','Disbursements'], 'Obligations', id={'name':'spnd_type_dash',
                                                                                                   'type':'filter-dropdown',
                                                                                                   'index':1}),
                                html.H5('Year:', style={"margin-top": "5px"}),
                                dcc.Dropdown(df_yrs, 'All', id={'name':'year_dash',
                                                                 'type':'filter-dropdown',
                                                                 'index':2}),
                                html.H5('Year Calculation:', style={"margin-top": "5px"}),
                                dcc.Dropdown(['Transaction Fiscal Year',
                                              'Award Start Year'], 'Transaction Fiscal Year', id={'name':'year_type_dash',
                                                                                                  'type':'filter-dropdown',
                                                                                                  'index':3}),
                                dbc.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"margin-top": "5px"}),
                            ]
                        ),
                    ],
                    style={"margin-top":"5px"},
                ),
                ], style=SIDEBAR_STYLE
            ),
            html.Div(children=[
                html.H4('Data Comparison Introduction:', style={"margin-top":"25px"}
                        ),
                html.P('''The purpose of the data comparison dropdown is to provide members of the F-Data team the ability to visualize, understand,
                          and ask questions of quarterly Department of State foreign assistance data.'''),
                html.P('''\n\nThe first two options of this dropdown show spending patterns at the bureau, year, and location level
                          for both published and unpuplished data. Users can select either all obligated data or all disbursement data to see both what
                          has been committed and what has already been spent. Users can also group spending for internal data by the year
                          in which the transaction occurred or the year when the award was first obligated.'''),
                html.P('''\n\nhe third dropdown option, "Combined (Beta), allows users to create simple bar charts to directly compare between published and 
                          internal data. This functionality is still in development, so please report any found bugs.'''),
                html.P('''\n\nFor access to the full foreign assistance dataset, as well as documentation of what all columns mean and additional
                          visualization tools, visit https://foreignassistance.gov/''')]
                        ,) #style={'width': '64%', 'display':'inline-block', "margin-left": "15px"})
        ])
    elif tab == '/dqi':
        
        df = pd.concat([pd.read_feather(fr"{feather}/FADR_full_1"),pd.read_feather(fr"{feather}/FADR_full_2")]).reset_index(drop=True)

        df_burs = sorted(df['bureau'].astype(str).unique().tolist())
        df_yrs = sorted(df['year'].astype(str).unique().tolist())
        return html.Div(children=[
            html.Div(children=[
                html.H3('Filters:', style={"margin-top":"25px"}),
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5('Bureau:'),
                                dcc.Dropdown(df_burs, 'AF', id={'name':'bureau_dqi',
                                                                 'type':'filter-dropdown',
                                                                 'index':0}),
                                html.H5('Year:', style={"margin-top": "5px"}),
                                dcc.Dropdown(df_yrs, 'All', id={'name':'year_dqi',
                                                                 'type':'filter-dropdown',
                                                                 'index':2}),
                                dbc.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"margin-top": "5px"}),
                            ]
                        ),
                    ],
                    #style={'width': '33%','display': 'inline-block'},
                ), 
            ], style=SIDEBAR_STYLE
            ),
            html.Div(children=[
                html.H4('DQI Introduction:', style={"margin-top":"25px"}
                        ),
                html.P('''The purpose of this dashboard is to provide members of the F-Data team the ability to visualize, understand,
                          and ask questions of quarterly Department of State foreign assistance data.'''),
                html.P('''\n\nData Quality Improvement measures on this tab are designed to inform bureau outreach and measure 
                          progress in aligning foreign assistance data entry with US goals of accuracy and transparency.'''),
                html.P('''\n\nF-Data redactions refer to those redactions made by the F-Data team to mask sensitive info and PII in foreign 
                          assistance data. DATA Act redactions refer to those transactions marked sensitive by those responsible for entering 
                          foreign assistance transactions into the system of record. Below Length Requirement refers to those transactions 
                          where Award Description falls below the recommended length requirement set by IATI.''')]
                        ,#style={'width': '64%', 'display':'inline-block', "margin-left": "15px"}
                        )
        ])
    elif tab == '/query':
        all_options = {
            'Internal (FADR)': ['bureau','year','Location','US Sector','Funding Account'],
            'FA.gov (FAID)': ['bureau', 'Fiscal Year', 'Country Name', 'US Sector','Funding Account']
        }

        return html.Div(children=[
            html.Div(children=[
                html.H3('Filters:', style={"margin-top":"25px"}),
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5('Select Source:'),
                                dcc.RadioItems(
                                    list(all_options.keys()),
                                    'Internal (FADR)',
                                    inline=True,
                                    id={'name':'sources-radio',
                                        'type':'filter-dropdown',
                                        'index':0},
                                    labelStyle={"margin-right": "12px"}
                                ),
                                html.H5('Funding Type:'),
                                dcc.RadioItems(
                                    list(['Obligations','Disbursements']),
                                    'Obligations',
                                    inline=True,
                                    id={'name':'sources-radio',
                                        'type':'filter-dropdown',
                                        'index':1},
                                    labelStyle={"margin-right": "12px"}
                                ),
                                html.Div(id='dropdown-container', children=[]),
                                dbc.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"margin-top": "5px"})
                            ]
                        )
                    ],
                    #style={'width': '33%','display': 'inline-block'},
                ),
                ], style=SIDEBAR_STYLE
            ),
            html.Div(children=[
                html.H4('Query Tool Introduction:', style={"margin-top":"25px"}
                        ),
                html.P('''The purpose of this dashboard is to provide members of the F-Data team the ability to visualize, understand,
                          and ask questions of quarterly US Government foreign assistance data. Upon clicking the "Submit" button,
                          a table will populate below with your selections. That table is also available to download as a CSV file
                          for further analysis/visualization needs.'''),
                html.P('''\n\nThis tool allows users to query published and internal data in order to respond to internal or
                          external data calls. Data is filterable by managing agency, bureau, year, sector, location, and funding account. 
                          Multiple values are selectable for each field.'''),
                html.P('''\n\nDirect comparisons between published and internal data require running two queries - one on each data source - 
                          and downloading both results. Direct comparisons are available only for Department of State data.''')]
                        ,#style={'width': '64%', 'display':'inline-block', "margin-left": "15px"}
                        )
        ])
    elif tab == '/combined':

        return html.Div(children=[
            html.Div(children=[
                html.H3('Filters:', style={"margin-top":"25px"}),
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5('Bureau:'),
                                dcc.Dropdown(options=[],value='All', id={'name':'bureau',
                                                                 'type':'filter-dropdown',
                                                                 'index':0}),
                                html.H5('Fiscal Year:', style={"margin-top": "5px"}),
                                dcc.Dropdown(options=[],value='All', id={'name':'years',
                                                                 'type':'filter-dropdown',
                                                                 'index':1}),
                                html.H5('Recipient Location:', style={"margin-top": "5px"}),
                                dcc.Dropdown(options=[],value='All', id={'name':'locations',
                                                                 'type':'filter-dropdown',
                                                                 'index':2}),
                                html.H5('SPSD Category:', style={"margin-top": "5px"}),
                                dcc.Dropdown(options=[],value='All',optionHeight=50, id={'name':'cats',
                                                                                          'type':'filter-dropdown',
                                                                                          'index':3}),
                                html.H5('SPSD Sector:', style={"margin-top": "5px"}),
                                dcc.Dropdown(options=[],value='All',optionHeight=50, id={'name':'spsds',
                                                                                          'type':'filter-dropdown',
                                                                                          'index':4}),
                                html.H5('Funding Account:', style={"margin-top": "5px"}),
                                dcc.Dropdown(options=[],value='All',optionHeight=75, id={'name':'accts',
                                                                                          'type':'filter-dropdown',
                                                                                          'index':5},
                                             style={'font-size':'1.2rem'}),
                                dbc.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"margin-top": "5px"}),
                            ]
                        ),
                    ],
                    #style={'width': '33%','display': 'inline-block'},
                ), 
            ], style=SIDEBAR_STYLE
            ),
            html.Div(children=[
                html.H4('Data Comparison Introduction:', style={"margin-top":"25px"}
                        ),
                html.P('''The purpose of the data comparison dropdown is to provide members of the F-Data team the ability to visualize, understand,
                          and ask questions of quarterly Department of State foreign assistance data.'''),
                html.P('''\n\nThe first two options of this dropdown show spending patterns at the bureau, year, and location level
                          for both published and unpuplished data. Users can select either all obligated data or all disbursement data to see both what
                          has been committed and what has already been spent. Users can also group spending for internal data by the year
                          in which the transaction occurred or the year when the award was first obligated.'''),
                html.P('''\n\nThe Third dropdown option, "Combined (Beta), allows users to create simple bar charts to directly compare between published and 
                          internal data. This functionality is still in development, so please report any found bugs.'''),
                html.P('''\n\nFor access to the full foreign assistance dataset, as well as documentation of what all columns mean and additional
                          visualization tools, visit https://foreignassistance.gov/''')]
                        ,#style={'width': '64%', 'display':'inline-block', "margin-left": "15px"}
                        )
        ])

@app.callback(Output('dropdown-container','children'),
              Input('url', 'pathname'),
              # Input('tabs-faid-fadr-tracking', 'value'),
              Input('dropdown-container','children'),
              Input('submit-button-state','n_clicks'),
              Input({'name':'sources-radio','type':'filter-dropdown','index':0},'value'),
              Input({'name':'sources-radio','type':'filter-dropdown','index':1},'value'))
def display_dropdowns(tab, children, clicks, val, val2):
    regions = pd.read_csv(fr'{feather}/country_region_xwalk.csv')
    region_dict = dict(zip(regions.Country, regions.Region))

    if val == 'FA.gov (FAID)':
        df = pd.concat([pd.read_feather(fr"{feather}/FAID_full_1"),pd.read_feather(fr"{feather}/FAID_full_2")]).reset_index(drop=True)
        df['Region'] = df['Country Name'].map(lambda x: region_dict.get(x,x))
        df.loc[df['Country Name'].isin(['PSE','INFORMATION REDACTED','nan']), 'Region'] = 'World'
        allocs = 'Transaction Type Name'
    elif val == 'Internal (FADR)':
        df = pd.concat([pd.read_feather(fr"{feather}/FADR_full_1"),pd.read_feather(fr"{feather}/FADR_full_2")]).reset_index(drop=True)
        df['Region'] = df['Location'].map(lambda x: region_dict.get(x,x))
        df.loc[df['Location'].isin(['PSE','INFORMATION REDACTED','nan']), 'Region'] = 'World'
        allocs = 'Award_Transaction_Type'
    if val2 == 'Obligations':
        df = df.loc[df[allocs].isin(['Obligations','Commitment'])]
    else:
        df = df.loc[~(df[allocs].isin(['Obligations','Commitment']))]
    
    all_options = {
        'Internal (FADR)': ['Managing Agency','bureau','year','Region','Location','SPSD Category','US Sector','Funding Account'],
        'FA.gov (FAID)': ['Managing Agency','bureau', 'Fiscal Year','Region', 'Country Name', 'SPSD Category', 'US Sector','Funding Account']
    }
        
    if ctx.triggered_id != 'submit-button-state':
        children = []
    
    selecteds = {}
    
    for i,v in enumerate(all_options[val]):
        try:
            df = df.loc[df[v].isin(children[i]['props']['children'][1]['props']['value'])]
            selecteds[v] = children[i]['props']['children'][1]['props']['value']
        except Exception:
            selecteds[v] = None
            
    children = []

    index = 1
    for i in all_options[val]:
        if i in ['US Sector','Funding Account','SPSD Category','Managing Agency']:
            new_dropdown = html.Div([
                html.H5(f'{i}:', style={"margin-top": "5px"}),
                dcc.Dropdown(
                qtk.create_list(df,i),
                optionHeight=75,
                value = selecteds[i],
                id={
                    'name': f'{i}_print',
                    'type': 'filter-dropdown',
                    'index': index
                    },
                multi=True,
                style={'font-size':'1.2rem'}
                )
            ])
        else:
            tit = i.title()
            new_dropdown = html.Div([
                html.H5(f'{tit}:', style={"margin-top": "5px"}),
                dcc.Dropdown(
                qtk.create_list(df,i),
                value = selecteds[i],
                id={
                    'name': f'{i}_print',
                    'type': 'filter-dropdown',
                    'index': index
                    },
                multi=True
                )
            ])
        index += 1
        children.append(new_dropdown)

    return children

@app.callback([Output({'name':'bureau','type':'filter-dropdown','index':0},'options'),
               Output({'name':'years','type':'filter-dropdown','index':1},'options'),
              Output({'name':'locations','type':'filter-dropdown','index':2},'options'),
              Output({'name':'cats','type':'filter-dropdown','index':3},'options'),
              Output({'name':'spsds','type':'filter-dropdown','index':4},'options'),
              Output({'name':'accts','type':'filter-dropdown','index':5},'options')],
              [Input('url', 'pathname'),
              Input({'name':ALL,'type':'filter-dropdown','index':ALL},'value'),])
def live_dropdowns(tab, val):
    
    df = pd.concat([pd.read_feather(fr"{feather}/FADR_full_1"),pd.read_feather(fr"{feather}/FADR_full_2")]).reset_index(drop=True)
    
    if val[0] not in [None, 'All']:
        df = df.loc[(df['bureau']==val[0])]
    if val[1] not in [None, 'All']:
        df = df.loc[(df['year']==val[1])]
    if val[2] not in [None, 'All']:
        df = df.loc[(df['Location']==val[2])]
    if val[3] not in [None, 'All']:
        df = df.loc[(df['SPSD Category']==val[3])]
    if val[4] not in [None, 'All']:
        df = df.loc[(df['US Sector']==val[4])]
    if val[5] not in [None, 'All']:
        df = df.loc[(df['Funding Account']==val[5])]

        
    df_burs = ['All'] + sorted(df['bureau'].astype(str).unique().tolist())
    df_yrs = ['All'] + sorted(df['year'].astype(str).unique().tolist())
    df_locs = ['All'] + sorted(df['Location'].astype(str).unique().tolist())
    df_cats = ['All'] + sorted(df['SPSD Category'].astype(str).unique().tolist())
    df_spsds = ['All'] + sorted(df['US Sector'].astype(str).unique().tolist())
    df_accts = ['All'] + sorted(df['Funding Account'].astype(str).unique().tolist())
    
    return df_burs,df_yrs,df_locs,df_cats,df_spsds,df_accts
        
                                                                                              
@app.callback(Output('tabs-content-graphs', 'children'),
              Input('url', 'pathname'),
              # Input('tabs-faid-fadr-tracking', 'value'),
              Input('submit-button-state', 'n_clicks'),
              State({'name':ALL,'type':'filter-dropdown','index':ALL},'value'))
# @cache.memoize(timeout=TIMEOUT)
def render_content(tab, button, vals): #bur, yr, alls, yrtp
    if tab == '/faid':
        
        df = pd.concat([pd.read_feather(fr"{feather}/FAID_full_1"),pd.read_feather(fr"{feather}/FAID_full_2")]).reset_index(drop=True)
        df = df.loc[df['Managing Agency']=='Department of State']

        return html.Div(children=[
            html.H3('Amount Spent by Bureau and Year (Current US Dollars)'),
            html.Div(children=[
                dcc.Graph(
                    figure=dat.bureau_spending(df, 'FAID', vals[0], vals[2], vals[1], vals[3]), #style={'width': '59%','display': 'inline-block'}
                ),
                dcc.Graph(
                    figure=dat.yearly_spending(df, 'FAID', vals[0], vals[2], vals[1], vals[3]), #style={'width': '39%','display': 'inline-block'}
                ),
            ]),
            html.Div(children=[
                html.H3('Amount Spent by Country and Region (Current US Dollars)'),
                dcc.Graph(
                    figure=dat.create_map(df, 'FAID', vals[0], vals[2], vals[1], vals[3]), #style={'width': '66%','display': 'inline-block'}
                ),
                html.P('Note: Map data includes only spending which data is available at the country label. The bar chart includes all data aggregated at the regional and global level.'),
                dcc.Graph(
                    figure=dat.create_map(df, 'FAID', vals[0], vals[2], vals[1], vals[3], mapping=False), #style={'width': '32%','display': 'inline-block'}
                )
            ]),
            html.Div(children=[
                html.H3('Amount Spent by SPSD Category (Current US Dollars)'),
                dcc.Graph(
                    figure=dat.SPSD_spending(df, 'FAID', vals[0], vals[2], vals[1], vals[3]), #style={'width': '66%','display': 'inline-block'}
                ),
            ])
        ],)
    elif tab == '/fadr':
        
        df = pd.concat([pd.read_feather(fr"{feather}/FADR_full_1"),pd.read_feather(fr"{feather}/FADR_full_2")]).reset_index(drop=True)

        return html.Div(className='row', children=[
            html.H3('Amount Spent by Bureau and Year (Current US Dollars)'),
            html.Div(children=[
                dcc.Graph(
                    figure=dat.bureau_spending(df, 'FADR', vals[0], vals[2], vals[1], vals[3]), #style={'width': '59%','display': 'inline-block'}
                ),
                dcc.Graph(
                    figure=dat.yearly_spending(df, 'FADR', vals[0], vals[2], vals[1], vals[3]), #style={'width': '39%','display': 'inline-block'}
                ),
            ]),
            html.Div(children=[
                html.H3('Amount Spent by Country and Region (Current US Dollars)'),
                dcc.Graph(
                    figure=dat.create_map(df, 'FADR', vals[0], vals[2], vals[1], vals[3]), #style={'width': '66%','display': 'inline-block'}
                ),
                html.P('Note: Map data includes only spending which data is available at the country label. The bar chart includes all data aggregated at the regional and global level.'),
                dcc.Graph(
                    figure=dat.create_map(df, 'FADR', vals[0], vals[2], vals[1], vals[3], mapping=False), #style={'width': '32%','display': 'inline-block'}
                )
            ]),
            html.Div(children=[
                html.H3('Amount Spent by SPSD Category (Current US Dollars)'),
                dcc.Graph(
                    figure=dat.SPSD_spending(df, 'FADR', vals[0], vals[2], vals[1], vals[3]), #style={'width': '66%','display': 'inline-block'}
                ),
            ])
        ])
    elif tab == '/dqi':
        return html.Div(className='row', children=[
            html.H3('Bureau DQI Progress Dashboard'),
            html.Div(children=[
                dcc.Graph(
                    figure=dqi.find_bureau(vals[0]), #style={'width': '99%','display': 'inline-block'}
                ),
                html.P('Note: Percentage values for F-Data are calculated as (# Redactions / # Transactions). Multiple fields needing redaction in a single transaction can result in values greater than 100%.'),
                # dbc.Table.from_dataframe(dqi.common_pii(vals[0],vals[1]), style={'width': '32%','display': 'inline-block'}
                # )
            ]),
            html.Div(children=[
                dcc.Graph(
                    figure=dqi.redaction_type(vals[0],vals[1],condensed=False), style={"margin-top": "15px"}#style={'width': '30%','display': 'inline-block'}
                ),
                dcc.Graph(
                    figure=dqi.redaction_type(vals[0],vals[1]), #style={'width': '31%','display': 'inline-block'}
                ),
                dcc.Graph(
                    figure=dqi.redaction_column(vals[0],vals[1]), #style={'width': '39%','display': 'inline-block'}
                ),
            ]),
        ])
    elif tab == '/query':
        regions = pd.read_csv(fr'{feather}/country_region_xwalk.csv')
        region_dict = dict(zip(regions.Country, regions.Region))
        if vals[0] == 'FA.gov (FAID)':
            df = pd.concat([pd.read_feather(fr"{feather}/FAID_full_1"),pd.read_feather(fr"{feather}/FAID_full_2")]).reset_index(drop=True)
            df['Region'] = df['Country Name'].map(lambda x: region_dict.get(x,x))
            df.loc[df['Country Name'].isin(['PSE','INFORMATION REDACTED','nan']), 'Region'] = 'World'
            allocs = 'Transaction Type Name'
        elif vals[0] == 'Internal (FADR)':
            df = pd.concat([pd.read_feather(fr"{feather}/FADR_full_1"),pd.read_feather(fr"{feather}/FADR_full_2")]).reset_index(drop=True)
            df['Region'] = df['Location'].map(lambda x: region_dict.get(x,x))
            df.loc[df['Location'].isin(['PSE','INFORMATION REDACTED','nan']), 'Region'] = 'World'
            allocs = 'Award_Transaction_Type'
        
        if vals[1] == 'Obligations':
            df = df.loc[df[allocs].isin(['Obligations','Commitment'])]
        else:
            df = df.loc[~(df[allocs].isin(['Obligations','Commitment']))]
        
        if any(isinstance(i, list) for i in vals):
            df = qtk.subset_data(df,vals[0],vals[2],vals[3],vals[4],vals[6],vals[7],vals[8],vals[9],reg=vals[5])
            return html.Div(className='row', children=[
                html.H3('FAID & FADR Query Tool'),
                dash_table.DataTable(id='query_results',
                                     data=df.to_dict('records'),
                                     columns=[{"name": i, "id": i} for i in df.columns],
                                     export_format="csv"
                                    )
            ])
        return html.Div(className='row', children=[
            html.H3('FAID & FADR Query Tool')
        ]),
    elif tab == '/combined':
        
        faid = pd.concat([pd.read_feather(fr"{feather}/FAID_full_1"),pd.read_feather(fr"{feather}/FAID_full_2")]).reset_index(drop=True)
        faid = faid.loc[faid['Managing Agency']=='Department of State']
        fadr = pd.concat([pd.read_feather(fr"{feather}/FADR_full_1"),pd.read_feather(fr"{feather}/FADR_full_2")]).reset_index(drop=True)

        if any(i!='All' for i in vals):

            return html.Div(className='row', children=[
                    html.H3('Data Source Comparison:'),
                    dcc.Graph(figure=qtk.create_chart(fadr,faid,[vals[0]],[vals[1]],[vals[2]],[vals[3]],[vals[4]],[vals[5]]))
                ])
        return html.Div(className='row', children=[
            html.H3('Data Source Comparison:')
        ])

if __name__ == '__main__':
    app.run_server(debug=False)
