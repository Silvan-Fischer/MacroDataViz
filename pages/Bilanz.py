import streamlit as st
import pandas as pd
import altair as alt
import requests


st.set_page_config(page_title="Bilanz", layout="wide")


@st.experimental_memo
def get_snb_data():
    data = pd.read_csv("https://data.snb.ch/api/cube/snbbipo/data/csv/de", header=2, delimiter=";")
    return data

data = get_snb_data()

@st.experimental_memo
def get_snb_dimensions():
    url = "https://data.snb.ch/api/cube/snbbipo/dimensions/de"
    data_dimensions = requests.get(url).json()
    data_dimensions = data_dimensions["dimensions"]
    dimensions = pd.json_normalize(data_dimensions,
        record_path=["dimensionItems", "dimensionItems"], 
        meta=[
            "name",
            ["dimensionItems","name"]
            ],
        meta_prefix='meta_'
    )
    return dimensions

dimensions = get_snb_dimensions()

data =  pd.merge(data,dimensions, how='left',left_on='D0',right_on='id', copy=False).drop('id', axis=1)

selection = alt.selection_single(on='mouseover', empty="none")
hightlight = alt.condition(selection, alt.value('black'), alt.Color('D0:N', legend=None))

aktive = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=["GFG", "D", "RIWF", "IZ", "W", "FRGSF", "FRGUSD", "GSGSF", "IG", "GD", "FI", "WSF", "DS", "UA"])
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': "Value_1"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': "Value_3"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': "Value_12"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': "Value_120"}],
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
    scale=alt.Scale(reverse=True, domainMin=0), axis=alt.Axis(orient="top", title="Monatsende | In Millionen Franken" , ticks=True, tickSize=10, tickColor="#e6eaf1"), sort=alt.EncodingSortField(field='Value', order='ascending')),
    alt.Y('Date:O',
    scale=alt.Scale(reverse=True,), axis=alt.Axis(title=None)),
    color=hightlight,
    tooltip=['Date:O', 'name', alt.Tooltip('Value:Q', format=',.0f'), alt.Tooltip('Share:Q', format='.1%'), alt.Tooltip('MoM:Q', format='.1%'), alt.Tooltip('QoQ:Q', format='.1%'), alt.Tooltip('YoY:Q', format='.1%'), alt.Tooltip('Yo10Y:Q', format='.1%')]
).add_selection(
    selection
)

aktive_total = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=["T0"])
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': "Value_1"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': "Value_3"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': "Value_12"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': "Value_120"}],
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

passive = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=["N", "GB", "VB", "GBI", "US", "VRGSF", "ES", "UT", "VF", "AIWFS", "SP", "RE"])
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': "Value_1"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': "Value_3"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': "Value_12"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': "Value_120"}],
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
    scale=alt.Scale(domainMin=0), axis=alt.Axis(orient="top", title="Monatsende | In Millionen Franken" , ticks=True, tickSize=10, tickColor="#e6eaf1"), sort=alt.EncodingSortField(field='Value', order='ascending')),
    alt.Y('Date:O',
    scale=alt.Scale(reverse=True,), axis=alt.Axis(orient="right", title=None)),
    color=hightlight,
    tooltip=['Date:O', 'name', alt.Tooltip('Value:Q', format=',.0f'), alt.Tooltip('Share:Q', format='.1%'), alt.Tooltip('MoM:Q', format='.1%'), alt.Tooltip('QoQ:Q', format='.1%'), alt.Tooltip('YoY:Q', format='.1%'), alt.Tooltip('Yo10Y:Q', format='.1%')]
).add_selection(
    selection
)

passive_total = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=["T1"])
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': "Value_1"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': "Value_3"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': "Value_12"}],
    groupby = ['D0']
).transform_window(
    window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': "Value_120"}],
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

col1, col2 = st.columns(2)

with col1:
   st.header("Aktive")
   st.altair_chart(aktive + aktive_total, use_container_width=True)

with col2:
   st.header("Passive")
   st.altair_chart(passive + passive_total, use_container_width=True)


#TODO: Add total as tick
# https://altair-viz.github.io/gallery/layered_chart_bar_mark.html?highlight=tick


st.dataframe(data)