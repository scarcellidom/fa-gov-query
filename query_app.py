from dash import Dash, dcc, html, ALL, dash_table, ctx
# import dash_auth
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import warnings
import data_tracking as dat
import query_tracking as qtk

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

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
    "zIndex": 10000,
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-top": "2rem",
    "margin-left": "33rem",
    "margin-right": "1rem",
    # "padding": "2rem 1rem",
}

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO, 'https://codepen.io/chriddyp/pen/bWLwgP.css'], suppress_callback_exceptions=True)

app.layout = html.Div(className='row', children=[
    dcc.Location(id='url'),
    dbc.NavbarSimple(children=[
            dbc.NavItem(dbc.NavLink("QUERY Tool (Beta)", href="/query",external_link=True, active="exact")),
            
        ],
        brand='F-Data',
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
    html.Div(children=[html.P('''\n\n\nPublished FA.gov data is current as of the website on 11 July 2023.''')], style={"margin-top": "25px"})
], style=CONTENT_STYLE)#style={"border":"10px white solid",'display': 'inline-block'})

server = app.server
                                                                                          
@app.callback(Output('tabs-content-dropdowns','children'),
              Input('url','pathname'))

def render_tabs(tab):
    if tab == '/':
        return html.Div(children=[
            html.Div(children=[
                        html.H3('F-Data:', style={'margin-top':'25px'}),
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
                            html.Div(
                                html.A("F-Data Hub", href="https://usdos.sharepoint.com/sites/F/SitePages/F-Data.aspx?from=SendByEmail&xsdata=MDV8MDF8fDIxODgzYTU1YWY5MTRlMTgyODE1MDhkYjg4N2Q1Mzc3fDY2Y2Y1MDc0NWFmZTQ4ZDFhNjkxYTEyYjIxMjFmNDRifDB8MHw2MzgyNTM4NDQwNTU2NjQ2NjF8VW5rbm93bnxWR1ZoYlhOVFpXTjFjbWwwZVZObGNuWnBZMlY4ZXlKV0lqb2lNQzR3TGpBd01EQWlMQ0pRSWpvaVYybHVNeklpTENKQlRpSTZJazkwYUdWeUlpd2lWMVFpT2pFeGZRPT18MXxMMk5vWVhSekx6RTVPak5sWm1FeE1XTTRMVEZrTldRdE5HSTJOQzFoT0daakxUZ3hZV1l3TmpGa1lXRXpORjlsWWpGaU9HRTJOeTFoTnpCaUxUUXlNV1F0T0RFeVl5MW1NMkl6WW1JNE1EWTFNemRBZFc1eExtZGliQzV6Y0dGalpYTXZiV1Z6YzJGblpYTXZNVFk0T1RjNE56WXdORGM0Tmc9PXwwN2YyY2Y0NjQ5MzY0YzViMjgxNTA4ZGI4ODdkNTM3N3w0ODQ3ZmY4YTRmN2I0ZjZjODRhOGI2OTFlNjZhMzg1Nw%3d%3d&sdata=RFRSWVJTK2REeno4N0VGVE5RWTRVQmwrdUdYN2Q5SlBsZG9vRFE2ajhVMD0%3d&ovuser=66cf5074-5afe-48d1-a691-a12b2121f44b%2cMacdonaldCL%40state.gov&OR=Teams-HL&CT=1689795677959&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIxNDE1LzIzMDYwNDAxMTM4IiwiSGFzRmVkZXJhdGVkVXNlciI6ZmFsc2V9&SafelinksUrl=https%3a%2f%2fusdos.sharepoint.com%2fsites%2fF%2fSitePages%2fF-Data.aspx")
                            ),
                ])
            ],style=SIDEBAR_STYLE),
            html.Div(children=[
                html.H5('Welcome to the FA.gov Query Tool'),
                html.Div(children=[
                        html.P('''The purpose of this app is to provide individuals at the State Department the ability to query
                                  and ask questions of FA.gov financial foreign assistance data.'''),
                        html.P('''\n\nThe Query tab allows users to query published data in order to respond to internal or
                                  external data calls. Data is filterable by agency, bureau, year, sector, funding account, and location. Multiple values are selectable 
                                  for each field.'''),
                        html.P('''\n\nFor access to the full foreign assistance dataset, as well as documentation of what all columns mean and additional
                                  visualization tools, visit https://foreignassistance.gov/''')
                    ], style={'margin-top':'25px','font-size':'14px'}),
                # dcc.Link(html.Button("QUERY BUILDER"), href="/query", refresh=True, style={'margin-top': '10px',
                #                                                                            'margin-bottom': '10px',
                #                                                                            'textAlign':'center',
                #                                                                            'margin':'auto'})
                # html.P('''\n[LARGE IMAGE WILL GO HERE]'''),
            ])
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
                                # html.H5('Select Source:'),
                                # dcc.RadioItems(
                                #     list(all_options.keys()),
                                #     'Internal (FADR)',
                                #     inline=True,
                                #     id={'name':'sources-radio',
                                #         'type':'filter-dropdown',
                                #         'index':0},
                                #     labelStyle={"margin-right": "12px"}
                                # ),
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
                html.P('''The purpose of this tool is to provide individuals at the State Department the ability to query
                          and ask questions of FA.gov financial foreign assistance data.'''),
                html.P('''\n\nThis tool allows users to query published data in order to respond to internal or
                          external data calls. Data is filterable by managing agency, bureau, year, sector, location, and funding account. 
                          Multiple values are selectable for each field. Leaving a filter blank is allowed and will not result in data being excluded. Upon clicking the "Submit" button,
                          a table will populate below with your selections. That table is also available to download as a CSV file
                          for further analysis/visualization needs.'''),
                html.P('''\n\nAfter clicking the submit button, the filters will update based on your existing criteria. For example,
                          selecting "Department of State" from the Managing Agency filter will update the Bureau filter to only show State
                          bureaus. This allows for preliminary data exploration and helps the user more easily select relevant fields. Users are
                          also able to choose "SELECT ALL" if they want all options included in the table but do not want to select them all individually.''')]
                        ,#style={'width': '64%', 'display':'inline-block', "margin-left": "15px"}
                        )
        ])
    
@app.callback(Output('dropdown-container','children'),
              Input('url', 'pathname'),
              Input('dropdown-container','children'),
              Input('submit-button-state','n_clicks'),
              Input({'name':'sources-radio','type':'filter-dropdown','index':1},'value'))
def display_dropdowns(tab, children, clicks, val2):
    regions = pd.read_csv(fr'{feather}/country_region_xwalk.csv')
    region_dict = dict(zip(regions.Country, regions.Region))

    df = pd.concat([pd.read_feather(fr"{feather}/FAID_full_1"),pd.read_feather(fr"{feather}/FAID_full_2")]).reset_index(drop=True)
    df['Region'] = df['Country Name'].map(lambda x: region_dict.get(x,x))
    df.loc[df['Country Name'].isin(['PSE','INFORMATION REDACTED','nan']), 'Region'] = 'World'
    allocs = 'Transaction Type Name'

    if val2 == 'Obligations':
        df = df.loc[df[allocs].isin(['Obligations','Commitment'])]
    else:
        df = df.loc[~(df[allocs].isin(['Obligations','Commitment']))]
    
    all_options = {
        'Internal (FADR)': ['Managing Agency','bureau','year','Region','Location','SPSD Category','US Sector','Funding Account'],
        'FA.gov (FAID)': ['Managing Agency','bureau', 'Fiscal Year','Region', 'Country Name', 'SPSD Category', 'US Sector','Funding Account']
    }
        
    val = 'FA.gov (FAID)'
    
    if ctx.triggered_id != 'submit-button-state':
        children = []
    
    selecteds = {}
    
    for i,v in enumerate(all_options[val]):
        try:
            if children[i]['props']['children'][1]['props']['value'] != ['SELECT ALL']:
                df = df.loc[df[v].isin(children[i]['props']['children'][1]['props']['value'])]
            else:
                selecteds[v] = None
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
                                                                                              
@app.callback(Output('tabs-content-graphs', 'children'),
              Input('url', 'pathname'),
              Input('submit-button-state', 'n_clicks'),
              State({'name':ALL,'type':'filter-dropdown','index':ALL},'value'))
def render_content(tab, button, vals): #bur, yr, alls, yrtp
    if tab == '/query':
        regions = pd.read_csv(fr'{feather}/country_region_xwalk.csv')
        region_dict = dict(zip(regions.Country, regions.Region))
        df = pd.concat([pd.read_feather(fr"{feather}/FAID_full_1"),pd.read_feather(fr"{feather}/FAID_full_2")]).reset_index(drop=True)
        df['Region'] = df['Country Name'].map(lambda x: region_dict.get(x,x))
        df.loc[df['Country Name'].isin(['PSE','INFORMATION REDACTED','nan']), 'Region'] = 'World'
        allocs = 'Transaction Type Name'
      
        if vals[0] == 'Obligations':
            df = df.loc[df[allocs].isin(['Obligations','Commitment'])]
        else:
            df = df.loc[~(df[allocs].isin(['Obligations','Commitment']))]
        
        if any(isinstance(i, list) for i in vals):
            df = qtk.subset_data(df,'FA.gov (FAID)',vals[1],vals[2],vals[3],vals[5],vals[6],vals[7],vals[8],reg=vals[4])
            return html.Div(className='row', children=[
                html.H3('FA.gov Query Tool'),
                dash_table.DataTable(id='query_results',
                                     data=df.to_dict('records'),
                                     columns=[{"name": i, "id": i} for i in df.columns],
                                     export_format="csv"
                                    )
            ])
        return html.Div(className='row', children=[
            html.H3('FA.gov Query Tool')
        ]),
    
if __name__ == '__main__':
    app.run_server(debug=True)
