import plotly.express as px
import pandas as pd
import glob
import os


STATE = r"C:/Users/dscarcelli002/OneDrive - Guidehouse/FADR Processing"
feather = r"C:/Users/dscarcelli002/OneDrive - Guidehouse/FAID/scripts/dashboard/caches"
# feather = "caches"

discrete_sequence = ['#18BC9C','#F39C12','#E74C3C',
                     '#2C3E50','#3498DB','gray','black',
                     'blue','green','yellow']

def find_bureau(b):
    '''import bureau dataset and merge files'''
    
    trained = [os.path.basename(i).split(".")[0] for i in glob.glob(fr"{feather}/redaction_tracker/training/*.csv")]
    
    try:
        post = pd.read_csv(fr"{feather}/redaction_tracker/post/{b}.csv")
        post = post.rename(columns={'size':'F-Data'})
        data_act = pd.read_csv(fr"{feather}/redaction_tracker/data_act/{b}.csv")
        data_act = data_act.rename(columns={'size':'DATA Act'})
        length = pd.read_csv(fr"{feather}/redaction_tracker/length/{b}.csv")
        length = length.rename(columns={'size':'Below Length Requirement'})
        
        full = post.merge(data_act, on='label').merge(length, on='label')

        if b in trained:
            print('test')
            training = pd.read_csv(fr"{feather}/redaction_tracker/training/{b}.csv")
            training = training.rename(columns={'size':'Post-Training'})
            full = full.merge(training, on='label', how='outer')
            full = full[['label','F-Data','DATA Act','Below Length Requirement','Post-Training']]
            full = full.rename(columns={'label':'Extract'})
            full['Date'] = ""
            full.loc[full['Extract'].str.contains("_1"), 'Date'] = '20' + full['Extract'].str[2:4]
            
            fig = px.line(full, x='Extract', y=['F-Data','DATA Act','Below Length Requirement','Post-Training'],
                          color_discrete_sequence=discrete_sequence,
                          markers=True,
                          custom_data=["Extract"])
            fig.update_layout(yaxis = {'tickformat': ',.0%'}, hovermode='closest')
            fig.update_traces(hovertemplate="Extract: %{customdata} <br>Percentage: %{y}")
            fig.update_yaxes(title='Percent of Records', visible=True, showticklabels=True)
            fig.update_xaxes(
                title='Date',
                ticktext=full['Date'].tolist(),
                tickvals=full['Extract'].tolist(),
            )

            
            return fig
            
        full = full[['label','F-Data','DATA Act','Below Length Requirement']]
        full = full.rename(columns={'label':'Extract'})
        full['Date'] = ""
        full.loc[full['Extract'].str.contains("_1"), 'Date'] = '20' + full['Extract'].str[2:4]

        fig = px.line(full, x='Extract', y=['F-Data','DATA Act','Below Length Requirement'],
                      color_discrete_sequence=discrete_sequence,
                      markers=True,
                      custom_data=["Extract"])
        fig.update_layout(yaxis = {'tickformat': '~%'}, hovermode="closest")

        fig.update_yaxes(title='Percent of Records', visible=True, showticklabels=True)
        fig.update_xaxes(
            title='Date',
            ticktext=full['Date'].tolist(),
            tickvals=full['Extract'].tolist(),
        )
        fig.update_traces(hovertemplate="Extract: %{customdata} <br>Percentage: %{y}")

            
        return fig
            
    except FileNotFoundError:
        return px.line(x=[0],y=[0])
    
def common_pii(b, yr):
    '''return list of most common PII for a given year or all years'''
    
    try:
        log = pd.read_csv(fr"{STATE}/logs/dscarcelli002/15-22/changes/{b}.csv")
        log = log.loc[log['redaction_type'].str.contains('Bureau')]
        
        if yr != "All":
            log['year'] = "20" + log['UNIQUE_ID'].str[:2]
            log = log[log['year']==yr]
        
        small = log.groupby(['redaction_type','PII'],as_index=False).size()
        small = small.sort_values(by='size', ascending=False)
        
        return small.loc[small['size']>5].head(10)
    
    except FileNotFoundError:
        return pd.DataFrame({'redaction_type':['none'],
                             'PII':['none'],
                             'size':['none']})

def redaction_type(b, yr, condensed=True):
    '''return pie chart breaking down redactions by type (PII vs. SBU)'''
    
    # df = pd.read_feather(fr"{feather}\pii_sbu")
    df = pd.read_feather(fr"{feather}/pii_sbu")
    
    if b == 'ALL':
        df = df[['redaction_type','year','size']]
        df = df.groupby(['redaction_type','year'], as_index=False).sum()
    else:
        df = df[df['bureau']==b]
        df = df[['redaction_type','year','size']]
    if yr != 'All':
        df = df[df['year']==yr]
        df = df[['redaction_type','size']]
        
    if condensed:
        pii_dict = {
                'Bureau: Inline': 'PII',
                'Universal: Phone Number': 'PII',
                'Universal: tilde (~)': 'PII',
                'Bureau: Column': 'SBU',
                'Universal: Roll-Up': 'SBU',
                'Universal: Implementer Type': 'SBU',
                'Universal: Email': 'PII',
                'Custom Redaction': 'SBU',
                'Bureau: Multi-Conditional': 'SBU',
                'Universal: PSC': 'PII',
            }
        df['pii/sbu'] = df['redaction_type'].map(lambda x: pii_dict.get(x,x))
        out = df.groupby(['pii/sbu'], as_index=False).sum()
        
        fig = px.pie(out, values='size', names='pii/sbu', title='Breakdown of FADR Redactions by PII/SBU',
                      color_discrete_sequence=discrete_sequence)
        return fig
    
    out = df.groupby(['redaction_type'], as_index=False).sum()
    fig = px.pie(out, values='size', names='redaction_type', title='Breakdown of FADR Redactions by Type',
                      color_discrete_sequence=discrete_sequence)
    return fig

def redaction_column(b, yr):
    '''return pie chart breaking down redactions by column'''
    
    # df = pd.read_feather(fr"{feather}\col_log")
    df = pd.read_feather(fr"{feather}/col_log")
    
    if b == 'ALL':
        df = df[['updated_column','year','size']]
        df = df.groupby(['updated_column','year'], as_index=False).sum()
    else:
        df = df[df['bureau']==b]
        df = df[['updated_column','year','size']]
    if yr != 'All':
        df = df[df['year']==yr]
        df = df[['updated_column','size']]
    
    out = df.groupby(['updated_column'], as_index=False).sum()
    fig = px.pie(out, values='size', names='updated_column', title='Breakdown of FADR Redactions by Column',
                      color_discrete_sequence=discrete_sequence)
    return fig
