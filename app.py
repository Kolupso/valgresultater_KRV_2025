import streamlit as st
import pandas as pd
import time
from databricks import sql
from streamlit_autorefresh import st_autorefresh

# ---- Connection Settings ----
SERVER_HOST = st.secrets["SERVER_HOST"]
HTTP_PATH = st.secrets["HTTP_PATH"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]


st.set_page_config(page_title="Databricks Dashboard", layout="wide")
st.title("Personlige stemmer 2025")

kommunalvalg_query = "SELECT * FROM workspace.valgresultat.personlige_stemmer_kv_2025"
regionvalg_query = "SELECT * FROM workspace.valgresultat.personlige_stemmer_rv_2025"

page_dict = {"Kommunalvalg": kommunalvalg_query, "Regionsrådsvalg": regionvalg_query}

# Page selector
table = st.sidebar.selectbox("Vælg tabel", ["Kommunalvalg", "Regionsrådsvalg"])

table_query = page_dict[f"{table}"]

st_autorefresh(interval=30_000, key=table)

with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
    with c.cursor() as cur:
        cur.execute(f"{table_query}")
        df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])

# --- Sidebar filters ---
st.sidebar.header("Filters")

filters = {}
for col in ['kommune', 'region', 'parti']:
    if col in df.columns:
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) <= 98:  # only make filters for categorical-like columns
            selected = st.sidebar.multiselect(f"{col}", unique_vals, default=unique_vals)
            filters[col] = selected

# --- Apply filters ---
for col, selected in filters.items():
    df = df[df[col].isin(selected)]

st.dataframe(df)
st.caption(f"Table: {table} | Last updated: {time.strftime('%H:%M:%S')}")

# streamlit run databricks_live_dashboard.py
