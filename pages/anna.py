import streamlit as st
import pandas as pd
import time
from databricks import sql
from streamlit_autorefresh import st_autorefresh

SERVER_HOST = st.secrets["SERVER_HOST"]
HTTP_PATH = st.secrets["HTTP_PATH"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]

st.set_page_config(page_title="Annas overblik", layout="wide")
st.title("Personlige stemmer 2025 - Annas overblik")

query = """
SELECT  parti as Parti,
        kandidat as Kandidat,
        antal_stemmer as `Antal stemmer`
FROM workspace.valgresultat.personlige_stemmer_krv_2025
WHERE anna_liste = 'Ja'
ORDER BY parti, kandidat;
"""

with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
    with c.cursor() as cur:
        cur.execute(query)
        df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])

st_autorefresh(interval=30_000)
st.dataframe(df)
st.caption(f"Last updated: {time.strftime('%H:%M:%S')}")
