import streamlit as st
import pandas as pd
import altair as alt
import requests
from utilities import Charts

st.set_page_config(page_title='Bilanz', layout='wide')

# Get Data from SNB API
@st.experimental_memo
def get_snb_data():
    data = pd.read_csv('https://data.snb.ch/api/cube/snbbipo/data/csv/de', header=2, delimiter=';')
    return data

data = get_snb_data()

# Get Data-Labels from SNB API
@st.experimental_memo
def get_snb_dimensions():
    url = 'https://data.snb.ch/api/cube/snbbipo/dimensions/de'
    data_dimensions = requests.get(url).json()
    data_dimensions = data_dimensions['dimensions']
    dimensions = pd.json_normalize(data_dimensions,
        record_path=['dimensionItems', 'dimensionItems'], 
        meta=[
            'name',
            ['dimensionItems','name']
            ],
        meta_prefix='meta_'
    )
    dimensions.drop(columns=['meta_name'], inplace=True)
    dimensions.rename(columns={"id": "position_id", "name": "position_name", "meta_dimensionItems.name": "position_category"}, inplace=True)
    return dimensions

dimensions = get_snb_dimensions()

# Add aditional dimensions not in original dataset
moneyness = {"position_id":{"0":"GFG","1":"D","2":"RIWF","3":"IZ","4":"W","5":"FRGSF","6":"FRGUSD","7":"GSGSF","8":"IG",
"9":"GD","10":"FI","11":"WSF","12":"DS","13":"UA","14":"T0","15":"N","16":"GB","17":"VB","18":"GBI",
"19":"US","20":"VRGSF","21":"ES","22":"UT","23":"VF","24":"AIWFS","25":"SP","26":"RE","27":"T1"}, 
"moneyness":{"0":"Restliche Positionen","1":"CHF Liquidität","2":"Restliche Positionen","3":"Restliche Positionen","4":"Restliche Positionen","5":"CHF Liquidität","6":"Restliche Positionen","7":"CHF Liquidität","8":"CHF Liquidität",
"9":"CHF Liquidität","10":"CHF Liquidität","11":"CHF Liquidität","12":"CHF Liquidität","13":"CHF Liquidität","14":"Restliche Positionen","15":"CHF Liquidität","16":"CHF Liquidität","17":"CHF Liquidität","18":"CHF Liquidität",
"19":"CHF Liquidität","20":"CHF Liquidität","21":"CHF Liquidität","22":"CHF Liquidität","23":"Restliche Positionen","24":"Restliche Positionen","25":"Restliche Positionen","26":"Restliche Positionen","27":"Restliche Positionen"}}

moneyness = pd.DataFrame.from_dict(moneyness)

# Create combined dataframe with data and labels
dimensions = pd.merge(dimensions, moneyness, how='left',left_on='position_id',right_on='position_id', copy=False)
data =  pd.merge(data,dimensions, how='left',left_on='D0',right_on='position_id', copy=False).drop('D0', axis=1)

# Define lists which are used to sort the dataframes and filer the data for the different charts
sort_a = ['D', 'GFG', 'RIWF', 'IZ', 'W', 'FRGSF', 'FRGUSD', 'GSGSF', 'IG', 'GD', 'FI', 'WSF', 'DS', 'UA']
sort_p = ['VRGSF', 'ES', 'GB', 'VB', 'GBI', 'US',  'UT', 'N', 'VF', 'AIWFS', 'SP', 'RE']

# Sort dataframe as needed for ordering of elements in visualisations
data.position_id = data.position_id.astype("category")
data.position_id = data.position_id.cat.set_categories(sort_a + sort_p + ["T0", "T1"])
data = data.sort_values(by=['Date','position_id'], ignore_index=True)

# Create datasubsets in oder to not exceed altair limit of 5000 rows
data_a = data[data['position_category'].isin(["Aktiven"])] 
data_p = data[data['position_category'].isin(["Passiven"])]

# Inject CSS into streamlit

st.markdown(""" <style>
form.vega-bindings {
  position: absolute;
  left: 10px;
  top: 0px;
}
</style> """, unsafe_allow_html=True)

# Define UI of streamlit app 

col1, col2 = st.columns(2)

with col1:
    tab11, tab12, tab13 = st.tabs(["Aktive  - Bilanz", "Zinsen", "Wechselkurse"])
   
    with tab11:
        with st.expander("Anleitung"):
            st.write('Mithilfe von Shift \u21E7 können mehrer Zeitreihen gleichzeititg ausgewählt werden')        
        st.markdown('''
            **Aktive - Bilanz**  
            Nationalbank | Monatsende | In Millionen Franken
            ''')
        st.altair_chart(Charts.balancesheet(data_a, sort_a, ['T0']), use_container_width=True)

    with tab12:
        st.header('Comming soon...')

    with tab13:
        st.header('Comming soon...')

with col2:
    tab21, tab22 = st.tabs(["Passive - Bilanz", "Passive - Flow Proxy"])
   
    with tab21:
        with st.expander("Anleitung"):
            st.write('Mithilfe von Shift \u21E7 können mehrer Zeitreihen gleichzeititg ausgewählt werden')
        st.markdown('''
            **Passive - Bilanz**  
            Nationalbank | Monatsende | In Millionen Franken
            ''')  
        st.altair_chart(Charts.balancesheet(data_p, sort_p, ['T1'], orient='right', reverse=False, offset=21), use_container_width=True)

    with tab22:
        with st.expander("Anleitung"):
            st.write('Mithilfe von Shift \u21E7 können mehrer Zeitreihen gleichzeititg ausgewählt werden')
        st.markdown('''
            **Passive - Flow Proxy**  
            Nationalbank | Veränderung seit Vormonatsende | In Millionen Franken
            ''')          
        st.altair_chart(Charts.flow(data_p, sort_p, orient='right', reverse=False, offset=21), use_container_width=True)

st.dataframe(data)