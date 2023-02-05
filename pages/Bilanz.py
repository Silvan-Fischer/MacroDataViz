import streamlit as st
import pandas as pd
import altair as alt
import requests


st.set_page_config(page_title='Bilanz', layout='wide')


@st.experimental_memo
def get_snb_data():
    data = pd.read_csv('https://data.snb.ch/api/cube/snbbipo/data/csv/de', header=2, delimiter=';')
    return data

data = get_snb_data()

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
    return dimensions

dimensions = get_snb_dimensions()

moneyness = {"id":{"0":"GFG","1":"D","2":"RIWF","3":"IZ","4":"W","5":"FRGSF","6":"FRGUSD","7":"GSGSF","8":"IG",
"9":"GD","10":"FI","11":"WSF","12":"DS","13":"UA","14":"T0","15":"N","16":"GB","17":"VB","18":"GBI",
"19":"US","20":"VRGSF","21":"ES","22":"UT","23":"VF","24":"AIWFS","25":"SP","26":"RE","27":"T1"}, 
"moneyness":{"0":"Else","1":"CHF","2":"Else","3":"Else","4":"Else","5":"CHF","6":"Else","7":"CHF","8":"CHF",
"9":"CHF","10":"CHF","11":"CHF","12":"CHF","13":"CHF","14":"Else","15":"CHF","16":"CHF","17":"CHF","18":"CHF",
"19":"CHF","20":"CHF","21":"CHF","22":"CHF","23":"Else","24":"Else","25":"Else","26":"Else","27":"Else"}}

moneyness = pd.DataFrame.from_dict(moneyness)
dimensions = pd.merge(dimensions, moneyness, how='left',left_on='id',right_on='id', copy=False)
data =  pd.merge(data,dimensions, how='left',left_on='D0',right_on='id', copy=False).drop('id', axis=1)

selection = alt.selection_single(on='mouseover', empty='none')
hightlight = alt.condition(selection, alt.value('black'), alt.Color('order:N', legend=None), sort='descending')

D0_filter_a = ['D', 'GFG', 'RIWF', 'IZ', 'W', 'FRGSF', 'FRGUSD', 'GSGSF', 'IG', 'GD', 'FI', 'WSF', 'DS', 'UA']

aktive = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=D0_filter_a)
).transform_calculate( 
    order=f"indexof({D0_filter_a}, datum.D0)"
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': 'Value_3'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': 'Value_12'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': 'Value_120'}],
    groupby = ['D0']
).transform_window(
    Total='sum(Value)',
    groupby=['Date'],
    frame=[None, None]
).transform_calculate(
    MoM = (alt.datum.Value - alt.datum.Value_1) / alt.datum.Value_1,
    QoQ = (alt.datum.Value - alt.datum.Value_3) / alt.datum.Value_3,
    YoY = (alt.datum.Value - alt.datum.Value_12) / alt.datum.Value_12,
    Yo10Y = (alt.datum.Value - alt.datum.Value_120) / alt.datum.Value_120,
    Share = alt.datum.Value / alt.datum.Total
).mark_bar(opacity=0.8
).encode(
    alt.X('Value:Q',
    scale=alt.Scale(reverse=True, domainMin=0), axis=alt.Axis(orient='top', title='Monatsende | In Millionen Franken' , ticks=True, tickSize=10, tickColor='#e6eaf1')),
    alt.Y('Date:O',
    scale=alt.Scale(reverse=True,), axis=alt.Axis(title=None)),
    order='order:O',
    color=hightlight,
    tooltip=['Date:O', 'name', alt.Tooltip('Value:Q', format=',.0f'), alt.Tooltip('Share:Q', format='.1%'), alt.Tooltip('MoM:Q', format='.1%'), alt.Tooltip('QoQ:Q', format='.1%'), alt.Tooltip('YoY:Q', format='.1%'), alt.Tooltip('Yo10Y:Q', format='.1%')]
).add_selection(
    selection
)

aktive_total = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=['T0'])
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': 'Value_3'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': 'Value_12'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': 'Value_120'}],
    groupby = ['D0']
).transform_window(
    Total='sum(Value)',
    groupby=['Date'],
    frame=[None, None]
).transform_calculate(
    MoM = (alt.datum.Value - alt.datum.Value_1) / alt.datum.Value_1,
    QoQ = (alt.datum.Value - alt.datum.Value_3) / alt.datum.Value_3,
    YoY = (alt.datum.Value - alt.datum.Value_12) / alt.datum.Value_12,
    Yo10Y = (alt.datum.Value - alt.datum.Value_120) / alt.datum.Value_120,
    Share = alt.datum.Value / alt.datum.Total
).mark_tick(
    color='black',
    thickness=3
).encode(
    x='Value:Q',
    y='Date:O',
    tooltip=['Date:O', 'name', alt.Tooltip('Value:Q', format=',.0f'), alt.Tooltip('Share:Q', format='.1%'), alt.Tooltip('MoM:Q', format='.1%'), alt.Tooltip('QoQ:Q', format='.1%'), alt.Tooltip('YoY:Q', format='.1%'), alt.Tooltip('Yo10Y:Q', format='.1%')]
)

D0_filter_p = ['VRGSF', 'ES', 'GB', 'VB', 'GBI', 'US',  'UT', 'N', 'VF', 'AIWFS', 'SP', 'RE']

passive = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=D0_filter_p)
).transform_calculate( 
    order=f"indexof({D0_filter_p}, datum.D0)"
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': 'Value_3'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': 'Value_12'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': 'Value_120'}],
    groupby = ['D0']
).transform_window(
    Total='sum(Value)',
    groupby=['Date'],
    frame=[None, None]
).transform_calculate(
    MoM = (alt.datum.Value - alt.datum.Value_1) / alt.datum.Value_1,
    QoQ = (alt.datum.Value - alt.datum.Value_3) / alt.datum.Value_3,
    YoY = (alt.datum.Value - alt.datum.Value_12) / alt.datum.Value_12,
    Yo10Y = (alt.datum.Value - alt.datum.Value_120) / alt.datum.Value_120,
    Share = alt.datum.Value / alt.datum.Total
).mark_bar(opacity=0.8
).encode(
    alt.X('Value:Q',
    scale=alt.Scale(domainMin=0), axis=alt.Axis(orient='top', title='Monatsende | In Millionen Franken' , ticks=True, tickSize=10, tickColor='#e6eaf1')),
    alt.Y('Date:O',
    scale=alt.Scale(reverse=True,), axis=alt.Axis(orient='right', title=None)),
    color=hightlight,
    order='order:O',
    tooltip=['Date:O', 'name', alt.Tooltip('Value:Q', format=',.0f'), alt.Tooltip('Share:Q', format='.1%'), alt.Tooltip('MoM:Q', format='.1%'), alt.Tooltip('QoQ:Q', format='.1%'), alt.Tooltip('YoY:Q', format='.1%'), alt.Tooltip('Yo10Y:Q', format='.1%')]
).add_selection(
    selection
)

passive_total = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=['T1'])
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': 'Value_3'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': 'Value_12'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': 'Value_120'}],
    groupby = ['D0']
).transform_window(
    Total='sum(Value)',
    groupby=['Date'],
    frame=[None, None]
).transform_calculate(
    MoM = (alt.datum.Value - alt.datum.Value_1) / alt.datum.Value_1,
    QoQ = (alt.datum.Value - alt.datum.Value_3) / alt.datum.Value_3,
    YoY = (alt.datum.Value - alt.datum.Value_12) / alt.datum.Value_12,
    Yo10Y = (alt.datum.Value - alt.datum.Value_120) / alt.datum.Value_120,
    Share = alt.datum.Value / alt.datum.Total
).mark_tick(
    color='black',
    thickness=3
).encode(
    x='Value:Q',
    y='Date:O',
    tooltip=['Date:O', 'name', alt.Tooltip('Value:Q', format=',.0f'), alt.Tooltip('Share:Q', format='.1%'), alt.Tooltip('MoM:Q', format='.1%'), alt.Tooltip('QoQ:Q', format='.1%'), alt.Tooltip('YoY:Q', format='.1%'), alt.Tooltip('Yo10Y:Q', format='.1%')]
)

flow = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=D0_filter_p)
).transform_calculate( 
    order=f"indexof({D0_filter_p}, datum.D0)"
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': 'Value_3'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': 'Value_12'}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': 'Value_120'}],
    groupby = ['D0']
).transform_window(
    Total='sum(Value)',
    groupby=['Date'],
    frame=[None, None]
).transform_calculate(
    Flow = alt.datum.Value - alt.datum.Value_1,
    MoM = (alt.datum.Value - alt.datum.Value_1) / alt.datum.Value_1,
    QoQ = (alt.datum.Value - alt.datum.Value_3) / alt.datum.Value_3,
    YoY = (alt.datum.Value - alt.datum.Value_12) / alt.datum.Value_12,
    Yo10Y = (alt.datum.Value - alt.datum.Value_120) / alt.datum.Value_120,
    Share = alt.datum.Value / alt.datum.Total
).mark_bar(opacity=0.8
).encode(
    alt.X('Flow:Q',
    scale = alt.Scale(domain=[-200000, 200000]), axis=alt.Axis(orient='top', title='Veränderung seit Vormonatsende | In Millionen Franken' , ticks=True, tickSize=10, tickColor='#e6eaf1')),
    alt.Y('Date:O',
    scale=alt.Scale(reverse=True,), axis=alt.Axis(orient='right', title=None)),
    color=hightlight,
    order='order:O',
    tooltip=['Date:O', 'name', alt.Tooltip('Flow:Q', format='+.0f')]
).add_selection(
    selection
)

flow_total = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=D0_filter_p)
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
    groupby = ['D0']
).transform_calculate(
    Flow = alt.datum.Value - alt.datum.Value_1,
).transform_window(
    Total='sum(Flow)',
    groupby=['Date','moneyness'],
    frame=[None, None]
).mark_tick(
    color='black',
    thickness=3
).encode(
    x='Total:Q',
    y='Date:O',
    tooltip=['Date:O', alt.Tooltip('Total:Q', format=',.0f')]
)

flow_layer = alt.layer(flow, flow_total, data=data).facet(column = 'moneyness:N', columns=2)


col1, col2 = st.columns(2)

with col1:
    tab11, tab12, tab13 = st.tabs(["Aktive", "Zinsen", "Wechselkurse"])
   
    with tab11:
        st.header('Aktive')
        st.altair_chart(aktive + aktive_total, use_container_width=True)

    with tab12:
        st.header('Zinsen')

    with tab13:
        st.header('Wechselkurse') 

with col2:
    tab21, tab22 = st.tabs(["Passive", "Flow Proxy"])
   
    with tab21:
        st.header('Passive')
        st.altair_chart(passive + passive_total, use_container_width=True)

    with tab22:
        st.header('Flow Proxy')
        st.altair_chart(flow_layer, use_container_width=True)

st.dataframe(data)