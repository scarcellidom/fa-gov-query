import pandas as pd
import plotly.express as px
import warnings

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

def create_list(df, col):
    '''create dropdown list for the given column in the given dataframe'''
    
    return ['SELECT ALL'] + sorted(df[col].unique().tolist())

def subset_data(df, src, agen, burs, yrs, locs, cats, spsds, accts, reg=None, chart=False):
    '''subset dataset and calculate spending'''
    
    # set col names based on source
    bureau = 'bureau'
    if src == 'Internal (FADR)':
        year = 'year'
        location = 'Location'
        account = 'Funding Account'
        amount = 'Award_Transaction_Value'
    elif src == 'FA.gov (FAID)': 
        year = 'Fiscal Year'
        account = 'Funding Account'
        location = 'Country Name'
        amount = 'Current Dollar Amount'
    
    df = df.rename(columns={amount: 'Spending',
                            year: 'Fiscal Year',
                            location: 'Country/Region',
                            bureau: 'Bureau',
                            account: 'Funding Account'})
    
    # subset data based on dropdowns
    grp_cols = []
    if agen != ['All'] and agen != None:
        if 'SELECT ALL' not in agen:
            df = df.loc[df['Managing Agency'].isin(agen)]
        grp_cols.append('Managing Agency')
    if burs != ['All'] and burs != None:
        if 'SELECT ALL' not in burs:
            df = df.loc[df['Bureau'].isin(burs)]
        grp_cols.append('Bureau')
    if yrs != ['All'] and yrs != None:
        if 'SELECT ALL' not in yrs:
            df = df.loc[df['Fiscal Year'].astype(str).isin(yrs)]
        # df['Fiscal Year'] = df['Fiscal Year'].astype(str)
        grp_cols.append('Fiscal Year')
    if reg  != ['All'] and reg  != None:
        if 'SELECT ALL' not in reg:
            df = df.loc[df['Region'].isin(reg)]
        grp_cols.append('Region')
    if locs != ['All'] and locs != None:
        if 'SELECT ALL' not in locs:
            df = df.loc[df['Country/Region'].isin(locs)]
        grp_cols.append('Country/Region')
    if cats != ['All'] and cats != None:
        if 'SELECT ALL' not in cats:
            df = df.loc[df['SPSD Category'].isin(cats)]
        grp_cols.append('SPSD Category')
    if spsds != ['All'] and spsds != None:
        if 'SELECT ALL' not in spsds:
            df = df.loc[df['SPSD Code'].isin(spsds)]
        grp_cols.append('SPSD Code')
    if accts != ['All'] and accts != None:
        if 'SELECT ALL' not in accts:
            df = df.loc[df['Funding Account'].isin(accts)]
        grp_cols.append('Funding Account')
        
    # groupby
    subset = grp_cols + ['Spending']
    df = df[subset]
    df['Spending'] = df['Spending'].apply(lambda x: int(float(str(x).replace(",",""))))
    out = df.groupby(grp_cols, as_index=False).sum()
    if chart==False:
        out['Spending'] = '$' + out['Spending'].map('{:,.0f}'.format)

        # pivot and return
        if 'Fiscal Year' in grp_cols:
            grp_cols.remove('Fiscal Year')
            if len(grp_cols)>0:
                return out.pivot(index=grp_cols, columns='Fiscal Year', values='Spending').reset_index()
        return out
    out['Source'] = src
    return out

def create_chart(fadr, faid, burs, yrs, locs, cats, spsds, accts):
    '''make simple comparison bar chart for internal vs. published data'''
    default_color = "#18BC9C"
    
    out = pd.concat([subset_data(df=fadr,
                                 src='Internal (FADR)',
                                 agen=None,
                                 burs=burs,
                                 yrs=yrs,
                                 locs=locs,
                                 cats=cats,
                                 spsds=spsds,
                                 accts=accts,
                                 chart=True),
                     subset_data(df=faid,
                                 src='FA.gov (FAID)',
                                 agen=None,
                                 burs=burs,
                                 yrs=yrs,
                                 locs=locs,
                                 cats=cats,
                                 spsds=spsds,
                                 accts=accts,
                                 chart=True)])
    
    if len(out)>0:
        
        fig = px.bar(y=out['Spending'], x=out['Source'],
                     title='Published vs. Internal Comparison',
                     color_discrete_sequence=[default_color])
        fig.update_yaxes(title='Spending', visible=True, showticklabels=True)
        fig.update_xaxes(title='Source', visible=True, showticklabels=True)
        
        return fig
    
    fig = px.bar(x=[0],y=[0])
    fig.update_yaxes(title='Spending', visible=True, showticklabels=True)
    fig.update_xaxes(title='Source', visible=True, showticklabels=True)
    
    return fig