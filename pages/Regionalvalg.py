import streamlit as st
import pandas as pd
import time
from databricks import sql
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from zoneinfo import ZoneInfo

# ---- Connection Settings ----
SERVER_HOST = st.secrets["SERVER_HOST"]
HTTP_PATH = st.secrets["HTTP_PATH"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]

st.set_page_config(page_title="Regioner", layout="wide")
st.title("Personlige stemmer 2025 - Regioner")

# Select region
omraade = st.sidebar.selectbox("Vælg region", [
    "Region Nordjylland", "Region Syddanmark", "Region Midtjylland", "Region Østdanmark"
])

# Optional filter
sf_valg = st.sidebar.selectbox("Kun SF?", ["Ja", "Nej"])
sf_filter = " AND parti = 'F. SF - Socialistisk Folkeparti'" if sf_valg == "Ja" else ""

query = f"""
SELECT SUBSTRING_INDEX(parti, '.', 1) AS Partibogstav,
       SUBSTRING_INDEX(parti, '.', -1) AS Parti,
       kandidat as Kandidat,
       antal_stemmer as `Antal stemmer`
FROM workspace.valgresultat.personlige_stemmer_krv_2025
WHERE `kommune/region` = '{omraade}'
  AND `kommune/region` like '%Region%'
  AND kandidat != 'Listestemmer'
  {sf_filter}
ORDER BY parti, kandidat;
"""

sum_query = f"""
SELECT SUBSTRING_INDEX(parti, '.', 1) AS Partibogstav,
       SUBSTRING_INDEX(parti, '.', -1) AS Parti,
       SUM(antal_stemmer) as `Antal stemmer`
FROM workspace.valgresultat.personlige_stemmer_krv_2025
WHERE `kommune/region` = '{omraade}'
AND `kommune/region` like '%Region%'
GROUP BY parti
ORDER BY parti;
"""

with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
    with c.cursor() as cur:
        cur.execute(query)
        df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])

with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
    with c.cursor() as cur2:
        cur2.execute(sum_query)
        df_sum = pd.DataFrame(cur2.fetchall(), columns=[d[0] for d in cur2.description])

# Auto refresh
st_autorefresh(interval=30_000, key=omraade)

st.dataframe(df)
danish_time = datetime.now(ZoneInfo("Europe/Copenhagen")).strftime("%H:%M:%S")
st.caption(f"Kommune/region: {omraade} | Last updated: {danish_time}")
st.dataframe(df_sum)
