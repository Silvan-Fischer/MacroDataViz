import streamlit as st
import requests
import json
from dbnomics import fetch_series
import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)
import altair as alt

st.set_page_config(layout="wide")
st.title("DB Nomics Marco Data Vizualizer")

state = st.session_state
if 'provider_code' not in state:
    state['provider_code'] = ""
if 'provider_name' not in state:
    state['provider_name'] = ""
if 'dataset_code' not in state:
    state['dataset_code'] = ""
if 'dataset_name' not in state:
    state['dataset_name'] = ""

@st.experimental_memo
def get_providers():
    limts_providers = {"limit": "1000", "offset": "0"}
    request_providers = requests.get("https://api.db.nomics.world/v22/providers", 
                                     params=limts_providers)
    json_providers = json.loads(request_providers.text)
    providers = json_providers["providers"]["docs"]
    return [(provider["code"], provider["name"]) for provider in providers]

provider_details = get_providers()

selected_provider_name = st.selectbox(
    "Select a **provider**",
    [j for i, j in provider_details])

for item in provider_details:
    if item[1] == selected_provider_name:
        selected_provider_code = item[0]
        break

def change_provider(selected_provider_name, selected_provider_code):
    state['provider_name'] = selected_provider_name
    state['provider_code'] = selected_provider_code

st.button("**Load datasets**", on_click=change_provider, 
          args=(selected_provider_name, selected_provider_code,))

@st.experimental_memo
def get_datasets(provider_code):
    limts_datasets = {"limit": "500", "offset": "0"}
    request_datasets = requests.get(
        f"https://api.db.nomics.world/v22/datasets/{provider_code}",
        params=limts_datasets)
    json_datasets = json.loads(request_datasets.text)
    datasets = json_datasets["datasets"]["docs"]
    datasets_number = json_datasets["datasets"]["num_found"]
    dataset_details = [(dataset["code"], dataset["name"], dataset["nb_series"], 
                       dataset["nb_series"]) for dataset in datasets]
    return dataset_details, datasets_number

if state['provider_code'] == selected_provider_code:
    dataset_details, datasets_number = get_datasets(state['provider_code'])

if "dataset_details" not in globals():
   dataset_details = []
   selected_dataset_name = None
   selected_dataset_code = None
else:
    st.info(f"**Provider:** {state['provider_name']}"
            f"**Datasets:** {datasets_number}"
            f"**Link:** [DBNomics Provider Info]"
            f"(https://db.nomics.world/{state['provider_code']})"
            , icon="ℹ️")
    if datasets_number > 50:
        st.warning(f"This alpha version can only show the first 50 datasets "
                   f"of each provider. {state['provider_name']} "
                   f"has {datasets_number} datasets.")

selected_dataset_name = st.selectbox(
    "Select a **dataset**",
    [j for i, j, k, o in dataset_details])

for item in dataset_details:
    if item[1] == selected_dataset_name:
        selected_dataset_code = item[0]
        selected_dataset_series = item[2]
        selected_dataset_updated = item[3]
        break

if dataset_details != []:
    st.info(f"**Dataset Code:** {selected_dataset_code} "
            f"**Series in Dataset:** {selected_dataset_series} "
            f"**Last update:** {selected_dataset_updated} "
            f"**Link:** [DBNomics Dataset Info]('https://db.nomics.world/"
            f"{state['provider_code']}/"
            f"{selected_dataset_code}')", 
            icon="ℹ️")
    if selected_dataset_series > 2000:
        st.warning("This dataset has more than 2000 series."
                   " Loading can take some time and might not be successful.")


@st.experimental_memo
def get_dataset_data(provider_code, dataset_code):
    return fetch_series(provider_code, dataset_code, max_nb_series=10000)


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    # for col in df.columns:
    #     if is_object_dtype(df[col]):
    #         try:
    #             df[col] = pd.to_datetime(df[col])
    #         except Exception:
    #             pass

    #     if is_datetime64_any_dtype(df[col]):
    #         df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 40:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


def get_data(provider_code, dataset_code):
    df = get_dataset_data(provider_code, dataset_code)
    return filter_dataframe(df)

def change_dataset(selected_dataset_name, selected_dataset_code):
    state['dataset_name'] = selected_dataset_name
    state['dataset_code'] = selected_dataset_code

st.button("**Load data**",
    on_click=change_dataset,
    args=(selected_dataset_name,
    selected_dataset_code,))   

if state['dataset_code'] != "":
    data = get_data(state['provider_code'], state['dataset_code'])
    st.dataframe(data)

    brush = alt.selection(type='interval', encodings=['x'])
    selection = alt.selection_multi(fields=['series_code'], bind='legend')

    upper = alt.Chart(data).mark_line().encode(
        x = alt.X('period:T', scale=alt.Scale(domain=brush)),
        y = 'value:Q',
        color = "series_code:N",
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).properties(
        width=1000,
        height=300,
    ).add_selection(
    selection
    )
    

    lower = alt.Chart(data).mark_area().encode(
        x = 'period:T',
        y = 'max(value):Q'
    ).properties(
        width=1000,
        height=100,
    ).add_selection(brush)

    chart = upper & lower

    tab1, tab2 = st.tabs(["Chart 1", "Chart 2"])

    with tab1:
        st.altair_chart(chart, theme="streamlit", use_container_width=True)
    with tab2:
        st.write("Test")
