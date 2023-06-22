import plotly.express as px
import urllib.request
import pandas as pd
import numpy as np
import warnings
import json
import glob
import os
import shutil

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

user = os.path.expanduser('~').replace(os.sep, '/')
USAID = fr"{user}/OneDrive - Guidehouse/FAID/data"
STATE = fr"{user}/OneDrive - Guidehouse/FADR Processing"
# feather = fr"{user}/OneDrive - Guidehouse/FAID/scripts/dashboard/caches"
feather = "caches"

default_color = "#18BC9C"

def select_source(src):
    '''set FAID or FADR column names'''
    if src == 'FADR':
        locale = 'Location'
        amount = 'Award_Transaction_Value'
        bureau = 'bureau'
        time = 'year'
        allocs = 'Award_Transaction_Type'
        yrtype = 'Award_Start_Year'
    else:
        locale = 'Country Name'
        amount = 'Current Dollar Amount'
        bureau = 'bureau'
        time = 'Fiscal Year'
        allocs = 'Transaction Type Name'
        yrtype = 'Award_Start_Year'
        
    return locale, amount, bureau, time, allocs, yrtype

def create_map(df, src, bur, yr, alls, yrtp, mapping=True):
    '''create plotly map for spending by country'''
    locale, amount, bureau, time, allocs, yrtype = select_source(src)
    
    if src == 'FADR':
        df[amount] = df[amount].apply(lambda x: int(float(str(x).replace(",",""))))
    
    if bur != "All":
        df = df[df[bureau]==bur]
    if yrtp == 'Award Start Year':
        df['time'] = df['Award_Start_Year']
    if yr != "All":
        if yrtp == 'Award Start Year':
            df = df.loc[df['time'].astype(str)==yr]
        else:
            df = df.loc[df[time].astype(str)==yr]
    if alls == 'Obligations':
        df = df.loc[df[allocs].isin(['Obligations','Commitment'])]
        # df = df.loc[df[amount]>0]
    else:
        df = df.loc[~df[allocs].isin(['Obligations','Commitment'])]
        # df = df.loc[df[amount]>0]
    
    # Recipient_Location_Table = pd.read_csv(fr"{feather}\Country Code Table.csv", dtype=object, engine='c')
    Recipient_Location_Table = pd.read_csv(fr"{feather}/Country Code Table.csv", dtype=object, engine='c')
    Recipient_Location_Dict = dict(zip(Recipient_Location_Table.IATI, Recipient_Location_Table.ID))
    Backup_Dict = dict(zip(Recipient_Location_Table.Value, Recipient_Location_Table.ID))

    df['id'] = df[locale].map(lambda x: Recipient_Location_Dict.get(x,x))
    df['id'] = df['id'].map(lambda x: Backup_Dict.get(x,x))
    
    if mapping:
        codes = []
        # with urllib.request.urlopen(r"https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_admin_0_countries.geojson") as f:
        world_map = json.load(urllib.request.urlopen(r"https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_admin_0_countries.geojson"))
        # world_map = json.load(open(fr"{feather}\countries.geojson","r"))
        # world_map = json.load(open(fr"{feather}/countries.geojson","r"))
        for feature in world_map['features']:
            feature['id'] = feature['properties']['iso_a3']
            codes.append(feature['properties']['iso_a3'])

        df = df[['id',amount,locale]]
        df = df.groupby(['id',locale], as_index=False).sum()
        df['Spending'] = '$' + (df[amount]/1000000).round(2).astype(str) + 'MM'
        df['log_amt'] = np.log10(df[amount])
        
        df = df.loc[df['id'].isin(codes)]
        
        fig = px.choropleth(df,
                            locations='id',
                            geojson=world_map,
                            color='log_amt',
                            color_continuous_scale=px.colors.sequential.Darkmint,
                            hover_name=locale,
                            hover_data=['Spending'],
                            title='Spending by Location (hover to view)')
        fig.update_geos(fitbounds="locations", visible=True)
        fig.update_layout(margin=dict(l=60, r=60, t=50, b=50))
        fig.update(layout_coloraxis_showscale=False)
            
    else:
        # regions = pd.read_csv(fr'{feather}\country_region_xwalk.csv')
        regions = pd.read_csv(fr'{feather}/country_region_xwalk.csv')
        region_dict = dict(zip(regions.Country, regions.Region))

        # df = df.loc[~df['id'].isin(codes)]
        # df = df.loc[(df[locale]=='Worldwide') | (df[locale].str.contains('Region', case=False))].sort_values(by=amount, ascending=False)
        
        df['region'] = df[locale].map(lambda x: region_dict.get(x,x))
        df.loc[df[locale].isin(['PSE','INFORMATION REDACTED','nan']), 'region'] = 'World'
        df = df[[amount,'region']]
        df = df.groupby(['region'], as_index=False).sum()
        df = df.sort_values(by=amount, ascending=False)
        df['Spending'] = '$' + (df[amount]/1000000).round(2).astype(str) + 'MM'
        
        fig = px.bar(y=df[amount],x=df['region'],
                     title='Regional Spending Totals',
                     color_discrete_sequence=[default_color])
        fig.update_yaxes(title='Spending', visible=True, showticklabels=True)
        fig.update_xaxes(title='Region', visible=True, showticklabels=True)
        fig.update_traces(showlegend=False)
        fig.update(layout_coloraxis_showscale=False)
                
    return fig

# bureau spending
def bureau_spending(df, src, bur, yr, alls, yrtp):
    '''calculate spending by bureau and incorporate dropdowns'''
    locale, amount, bureau, time, allocs, yrtype = select_source(src)
    colors = {}
    if bur != "All":
        colors[bur] = "#F39C12"
    if yrtp == 'Award Start Year':
        df['time'] = df['Award_Start_Year']
    if yr != "All":
        if yrtp == 'Award Start Year':
            df = df.loc[df['time'].astype(str)==yr]
        else:
            df = df.loc[df[time].astype(str)==yr]
    if alls == 'Obligations':
        df = df.loc[df[allocs].isin(['Obligations','Commitment'])]
        # df = df.loc[df[amount]>0]
    else:
        df = df.loc[~df[allocs].isin(['Obligations','Commitment'])]
        # df = df.loc[df[amount]>0]
    
    color_discrete_map = {
        c: colors.get(c, default_color) 
        for c in df[bureau].unique()}
    
    df = df[[bureau,amount]]
    df[amount] = df[amount].apply(lambda x: int(float(str(x).replace(",",""))))
    df = df.groupby([bureau], as_index=False).sum()
    df = df.sort_values(by=amount, ascending=False)
    
    fig = px.bar(y=df[amount], x=df[bureau], color=df[bureau],
                 title='Spending by Bureau',
                 color_discrete_map=color_discrete_map)
    fig.update_yaxes(title='Spending', visible=True, showticklabels=True)
    fig.update_xaxes(title='Bureau', visible=True, showticklabels=True)
    fig.update_traces(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    return fig

#annual spending
def yearly_spending(df, src, bur, yr, alls, yrtp):
    '''calculate spending by year and incorporate dropdowns'''
    colors = {}
    locale, amount, bureau, time, allocs, yrtype = select_source(src)
    df['color'] = "default"

    if bur != "All":
        df = df[df[bureau]==bur]
    if yrtp == 'Award Start Year':
        df['time'] = df['Award_Start_Year']
    if yr != "All":
        if yrtp == 'Award Start Year':
            colors[yr] = "#F39C12"
            color_discrete_map = {
                c: colors.get(c, default_color) 
                for c in df['time'].astype(str).unique()}
        else:
            colors[yr] = "#F39C12"
            color_discrete_map = {
                c: colors.get(c, default_color) 
                for c in df[time].astype(str).unique()}
    else:
        color_discrete_map = {
            c: colors.get(c, default_color) 
            for c in df[time].astype(str).unique()}
        
    if alls == 'Obligations':
        df = df.loc[df[allocs].isin(['Obligations','Commitment'])]
        # df = df.loc[df[amount]>0]
    else:
        df = df.loc[~df[allocs].isin(['Obligations','Commitment'])]
        # df = df.loc[df[amount]>0]
        
    if yrtp == 'Award Start Year':
        df = df[['time',amount]]
        df[amount] = df[amount].apply(lambda x: int(float(str(x).replace(",",""))))
        df = df.groupby(['time'], as_index=False).sum()
        
        fig = px.bar(y=df[amount], x=df['time'], color=df['time'].astype(str),
                     title='Spending by Year',
                     color_discrete_map=color_discrete_map)
        fig.update_yaxes(title='Spending', visible=True, showticklabels=True)
        fig.update_xaxes(title='Year', visible=True, showticklabels=True)
        fig.update_traces(showlegend=False)
        fig.update(layout_coloraxis_showscale=False)
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
    else:
        df = df[[time,amount]]
        df[amount] = df[amount].apply(lambda x: int(float(str(x).replace(",",""))))
        df = df.groupby([time], as_index=False).sum()
        
        fig = px.bar(y=df[amount], x=df[time], color=df[time].astype(str),
                     title='Spending by Year',
                     color_discrete_map=color_discrete_map)
        fig.update_yaxes(title='Spending', visible=True, showticklabels=True)
        fig.update_xaxes(title='Year', visible=True, showticklabels=True)
        fig.update_traces(showlegend=False)
        fig.update(layout_coloraxis_showscale=False)
        fig.update_layout(yaxis={'categoryorder':'total ascending'})

    return fig

def SPSD_spending(df, src, bur, yr, alls, yrtp):
    '''break down spending by SPSD category and incorporate dropdowns'''
    locale, amount, bureau, time, allocs, yrtype = select_source(src)
    
    if src == 'FADR':
        df[amount] = df[amount].apply(lambda x: int(float(str(x).replace(",",""))))
    
    if bur != "All":
        df = df[df[bureau]==bur]
    if yrtp == 'Award Start Year':
        df['time'] = df['Award_Start_Year']
    if yr != "All":
        if yrtp == 'Award Start Year':
            df = df.loc[df['time'].astype(str)==yr]
        else:
            df = df.loc[df[time].astype(str)==yr]
    if alls == 'Obligations':
        df = df.loc[df[allocs].isin(['Obligations','Commitment'])]
    else:
        df = df.loc[~df[allocs].isin(['Obligations','Commitment'])]
    
    df = df[[amount,'SPSD Category']]
    df = df.groupby(['SPSD Category'], as_index=False).sum()
    df = df.sort_values(by=amount, ascending=False)
    df['Spending'] = '$' + (df[amount]/1000000).round(2).astype(str) + 'MM'
    
    fig = px.bar(y=df[amount],x=df['SPSD Category'],
                 title='Regional Spending Totals',
                 color_discrete_sequence=[default_color])
    fig.update_yaxes(title='Spending', visible=True, showticklabels=True)
    fig.update_xaxes(title='SPSD Category', visible=True, showticklabels=True)
    fig.update_traces(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    
    return fig

if __name__ == '__main__':
    
    # import latest csv versions
    files = glob.glob(fr'{USAID}/*.zip')
    faid = pd.read_csv(max(files, key=os.path.getmtime))
    # faid = pd.read_csv(fr'{USAID}/FAID_121222_full.zip')
    faid['Managing Agency'] = faid['Managing Agency Name']
    # faid = faid[faid['Managing Agency Acronym']=='STATE']
    faid['bureau'] = faid['Managing Sub Agency Or Bureau 1']
    faid['SPSD Category'] = faid['US Category Name']
    faid['SPSD Category'] = faid['SPSD Category'].str.replace('Economic Development', 'Economic Growth')
    faid['SPSD Category'] = faid['SPSD Category'].str.replace('Program Support', 'Program Development and Oversight')
    faid['US Sector'] = faid['US Sector Name']
    faid['Activity Start Date'] = pd.to_datetime(faid['Activity Start Date'])
    faid['Award_Start_Year'] = faid['Activity Start Date'].dt.year.astype('Int64').astype(str)
    faid = faid[faid['Fiscal Year']>2014]
    faid['Fiscal Year'] = faid['Fiscal Year'].astype(str)
    
    Treasury_Account_Title_Table = pd.read_csv(fr"{STATE}/DATA/reference_maps/Treasury Account Title Table.csv", dtype =object, engine ='c')
    Treasury_Account_Dict = dict(zip(Treasury_Account_Title_Table.ID, Treasury_Account_Title_Table.Value))
    Treasury_Account_Dict['0040'] = 'United States Emergency Refugee and Migration Assistance Fund, Funds Appropriated to the President'
    Treasury_Account_Dict['0306'] = 'Assistance for Europe, Eurasia, and Central Asia, Funds Appropriated to the President, US Agency for International Development'
    Treasury_Account_Dict['1081'] = 'International Military Education and Training'
    Treasury_Account_Dict['1085'] = 'Foreign Military Financing, Direct Loan Program Account'

    faid['Funding Account'] = faid['Funding Account ID'].str.split("x").str[1]
    faid['Funding Account'] = faid['Funding Account'].map(lambda x: Treasury_Account_Dict.get(x,np.nan))
    faid['Funding Account'].fillna(faid['Funding Account Name'], inplace=True)
    
    fadr = pd.read_csv(fr'{STATE}/DATA/OUT/dscarcelli002/FADR_APP.zip') # need to manually update
    fadr['bureau'] = fadr['UNIQUE_ID'].str[3:6].str.strip('x')
    fadr['year'] = "20" + fadr['UNIQUE_ID'].str[:2]
    # fadr['year'] = fadr['year'].astype(int)
    # fadr['Award_Transaction_Date'] = pd.to_datetime(fadr['Award_Transaction_Date'])
    # fadr['month'] = fadr['Award_Transaction_Date'].dt.month.astype('Int64')
    # fadr.loc[fadr['month']>9, 'year'] += 1
    # fadr['year'] = fadr['year'].astype(str)
    
    fadr['Award_Start_Date'] = pd.to_datetime(fadr['Award_Start_Date'],errors='coerce')
    fadr['Award_Start_Year'] = fadr['Award_Start_Date'].dt.year.astype('Int64').astype(str)
    # fadr['Award_Start_Month'] = fadr['Award_Start_Date'].dt.month.astype('Int64')
    # fadr.loc[fadr['Award_Start_Month']>9, 'Award_Start_Year'] += 1
    # fadr['Award_Start_Year'] = fadr['Award_Start_Year'].astype(str)
    
    spsds = pd.read_csv(fr"{STATE}/DATA/reference_maps/DAC USG SPSD Map From Program Area.csv")
    spsd_dict = dict(zip(spsds.PROGRAM_AREA, spsds.DOS_SPSD_Official_Name))
    fadr['SPSD Category'] = fadr['PROGRAM_AREA'].astype(str).str.split(".").str[0]
    fadr['SPSD Category'] = fadr['SPSD Category'].map(lambda x: spsd_dict.get(x,'Multi-sector - Unspecified'))
    fadr['SPSD Category'] = fadr['SPSD Category'].str.replace(' - General', "")
    fadr['SPSD Category'] = fadr['SPSD Category'].str.replace(' - Unspecified', "")
    fadr['SPSD Category'] = fadr['SPSD Category'].str.replace('Economic Development', 'Economic Growth')
    fadr['US Sector'] = fadr['Award_Transaction_U_S_Foreign_Assistance_Sector_Code'].apply(lambda x: " - ".join(x.split(" - ")[1:]))
    fadr['Location'] = fadr['Benefitting Country/Region']
    fadr['Funding Account'] = fadr['Treasury_Account_Title']
    fadr['Managing Agency'] = 'Department of State'
    
    # subset data to only necessary columns
    faid_cols = [
            'Country Name',
            'Current Dollar Amount',
            'Managing Agency',
            'bureau',
            'Fiscal Year',
            'Transaction Type Name',
            'Award_Start_Year',
            'SPSD Category',
            'US Sector',
            'Funding Account'
        ]
    
    fadr_cols = [
            'Location',
            'Award_Transaction_Value',
            'Award_Transaction_Type',
            'Award_Start_Year',
            'Managing Agency',
            'bureau',
            'year',
            'SPSD Category',
            'US Sector',
            'Funding Account'
        ]
    
    burs = fadr['bureau'].unique().tolist()
    # faid = faid.loc[faid['bureau'].isin(burs)]
    faid = faid[faid_cols]
    faid_cols.remove('Current Dollar Amount')
    faid = faid.groupby(faid_cols, as_index=False).sum()
    faid1 = faid[:len(faid)//2].reset_index(drop=True)
    faid2 = faid[len(faid)//2:].reset_index(drop=True)
    
    fadr = fadr[fadr_cols]

    fadr = fadr.astype(str)
    fadr['Award_Transaction_Value'] = fadr['Award_Transaction_Value'].apply(lambda x: int(float(str(x).replace(",",""))))
    fadr_cols.remove('Award_Transaction_Value')
    fadr = fadr.groupby(fadr_cols, as_index=False).sum()
    fadr1 = fadr[:len(fadr)//2].reset_index(drop=True)
    fadr2 = fadr[len(fadr)//2:].reset_index(drop=True)
    
    # export to feather files
    faid1.to_feather(fr"{feather}/FAID_full_1", compression='zstd')
    faid2.to_feather(fr"{feather}/FAID_full_2", compression='zstd')
    fadr1.to_feather(fr"{feather}/FADR_full_1", compression='zstd')
    fadr2.to_feather(fr"{feather}/FADR_full_2", compression='zstd')
    
    # auxiliary dqi files
        
    all_logs = pd.concat([pd.read_csv(i) for i in glob.glob(fr'{STATE}/logs/dscarcelli002/15-22/changes/*.csv')])
    all_logs['bureau'] = all_logs['UNIQUE_ID'].str[3:6].str.strip("x")
    all_logs['year'] = "20" + all_logs['UNIQUE_ID'].str[:2]
    
    pii_sbu = all_logs[['bureau','redaction_type','year']]
    pii_sbu = pii_sbu.groupby(['bureau','redaction_type','year'], as_index=False).size()
    col_log = all_logs[['bureau','updated_column','year']]
    col_log = col_log.groupby(['bureau','updated_column','year'], as_index=False).size()
    
    pii_sbu.to_feather(fr"{feather}/pii_sbu", compression='zstd') # PII vs. SBU pie chart
    col_log.to_feather(fr"{feather}/col_log", compression='zstd') # Redacted field pie chart

    stats = ['data_act','length','post','training']
    shutil.copy(fr"{STATE}/DATA/reference_maps/training_tracker.xlsx",fr"{feather}/training_tracker.xlsx")
    for d in stats:
        os.chdir(fr"{STATE}/DATA/reference_maps/redaction_tracker/{d}")
        for f in glob.glob("*.csv"):
            shutil.copy(fr"{STATE}/DATA/reference_maps/redaction_tracker/{d}/{f}",fr"{feather}/redaction_tracker/{d}/{f}")
