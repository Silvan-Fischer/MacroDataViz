import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Bilanz", layout="wide")


@st.experimental_memo
def get_snb_data():
    data = pd.read_csv("https://data.snb.ch/api/cube/snbbipo/data/csv/de", header=2, delimiter=";")
    return data

data = get_snb_data()

selection = alt.selection_single(on='mouseover', empty="none")
hightlight = alt.condition(selection, alt.value('black'), alt.Color('D0:N', legend=None))

aktive = alt.Chart(data).mark_bar(opacity=0.8).encode(
    alt.X('Value:Q',
    scale=alt.Scale(domainMin=0), axis=alt.Axis(orient="top", title="Monatsende | In Millionen Franken" , ticks=True, tickSize=10, tickColor="#e6eaf1"), sort=alt.EncodingSortField(field='Value', order='ascending')),
    alt.Y('Date:O',
    scale=alt.Scale(reverse=True,), axis=alt.Axis(title=None)),
    color=hightlight
).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=["GFG", "D", "RIWF", "IZ", "W", "FRGSF", "FRGUSD", "GSGSF", "IG", "GD", "FI", "WSF", "DS", "UA"])
).add_selection(
    selection
)


passive = alt.Chart(data).mark_bar(opacity=0.8).encode(
    alt.X('Value:Q',
    scale=alt.Scale(reverse=True, domainMin=0), axis=alt.Axis(orient="top", title="Monatsende | In Millionen Franken", ticks=True, tickSize=10, tickColor="#e6eaf1")),
    alt.Y('Date:O',
    scale=alt.Scale(reverse=True,), axis=alt.Axis(orient="right", title=None)),
    color=hightlight
).transform_filter(
    alt.FieldOneOfPredicate(field='D0', oneOf=["N", "GB", "VB", "GBI", "US", "VRGSF", "ES", "UT", "VF", "AIWFS", "SP", "RE"])
).add_selection(
    selection
)


col1, col2 = st.columns(2)

with col1:
   st.header("Aktive")
   st.altair_chart(aktive, use_container_width=True)

with col2:
   st.header("Passive")
   st.altair_chart(passive, use_container_width=True)


#TODO: Add total as tick
# https://altair-viz.github.io/gallery/layered_chart_bar_mark.html?highlight=tick


st.dataframe(data)