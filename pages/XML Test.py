import streamlit as st
import pandas as pd

st.set_page_config(page_title="XML Interest Rates", layout="wide")

# Read the XLS file
with open('style.xsl', 'r') as f:
    xsl_str = f.read()

data = pd.read_xml("https://www.snb.ch/selector/de/mmr/intfeed/rss", stylesheet=xsl_str)
st.dataframe(data)