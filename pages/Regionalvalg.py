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

# query = f"""
# SELECT SUBSTRING_INDEX(parti, '.', 1) AS Partibogstav,
#        SUBSTRING_INDEX(parti, '.', -1) AS Parti,
#        kandidat as Kandidat,
#        antal_stemmer as `Antal stemmer`
# FROM workspace.valgresultat.personlige_stemmer_krv_2025
# WHERE `kommune/region` = '{omraade}'
#   AND `kommune/region` like '%Region%'
#   AND kandidat != 'Listestemmer'
#   {sf_filter}
# ORDER BY parti, kandidat;
# """

# sum_query = f"""
# SELECT SUBSTRING_INDEX(parti, '.', 1) AS Partibogstav,
#        SUBSTRING_INDEX(parti, '.', -1) AS Parti,
#        SUM(antal_stemmer) as `Antal stemmer`
# FROM workspace.valgresultat.personlige_stemmer_krv_2025
# WHERE `kommune/region` = '{omraade}'
# AND `kommune/region` like '%Region%'
# GROUP BY parti
# ORDER BY parti;
# """

# with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
#     with c.cursor() as cur:
#         cur.execute(query)
#         df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])

# with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
#     with c.cursor() as cur2:
#         cur2.execute(sum_query)
#         df_sum = pd.DataFrame(cur2.fetchall(), columns=[d[0] for d in cur2.description])


url = "https://raw.githubusercontent.com/Kolupso/valgresultater_KRV_2025/refs/heads/main/combined_results.csv"
df = pd.read_csv(url)
df["antal_stemmer"] = df["antal_stemmer"].astype(int)

df_filtered = df.copy()

# WHERE kommune/region = {omraade}
df_filtered = df_filtered[df_filtered["kommune/region"] == omraade]

# AND kommune/region like '%Region%'
df_filtered = df_filtered[df_filtered["kommune/region"].str.contains("Region")]

# AND kandidat != 'Listestemmer'
df_filtered = df_filtered[df_filtered["kandidat"] != "Listestemmer"]

# SUBSTRING_INDEX(parti,'.',1) → text before first dot
df_filtered["Partibogstav"] = df_filtered["parti"].str.split(".").str[0]

# AND possible extra SF filter
# `sf_filter` usually becomes: "df_filtered = df_filtered[df_filtered['SFU_kandidat']=='Ja']"
if sf_valg == "Ja":
    df_filtered = df_filtered[df_filtered["Partibogstav"] == "F"]

# SUBSTRING_INDEX(parti,'.',-1) → text after last dot
df_filtered["Parti"] = df_filtered["parti"].str.split(".").str[-1]

# SELECT columns + rename
df_filtered = (
    df_filtered
    .loc[:, ["Partibogstav", "Parti", "kandidat", "antal_stemmer"]]
    .rename(columns={
        "kandidat": "Kandidat",
        "antal_stemmer": "Antal stemmer"
    })
)

# ORDER BY parti, kandidat  (Parti and Kandidat now)
df_filtered = df_filtered.sort_values(["Parti", "Kandidat"]).reset_index(drop=True)


df_filtered2 = df.copy()

# WHERE kommune/region = '{omraade}'
df_filtered2 = df_filtered2[df_filtered2["kommune/region"] == omraade]

# AND kommune/region LIKE '%Region%'
df_filtered2 = df_filtered2[df_filtered2["kommune/region"].str.contains("Region")]

# GROUP BY parti → aggregate antal_stemmer
df_grouped = (
    df_filtered2
    .groupby("parti", as_index=False)
    .agg({"antal_stemmer": "sum"})
)

# SUBSTRING_INDEX(parti, '.', 1)
df_grouped["Partibogstav"] = df_grouped["parti"].str.split(".").str[0]

# SUBSTRING_INDEX(parti, '.', -1)
df_grouped["Parti"] = df_grouped["parti"].str.split(".").str[-1]

# SELECT and rename
df_grouped = df_grouped.rename(columns={"antal_stemmer": "Antal stemmer"})

df_grouped = df_grouped[["Partibogstav", "Parti", "Antal stemmer"]]

# ORDER BY parti
df_grouped = df_grouped.sort_values("Parti").reset_index(drop=True)


# Auto refresh
st_autorefresh(interval=30_000, key=omraade)

st.dataframe(df_filtered)
danish_time = datetime.now(ZoneInfo("Europe/Copenhagen")).strftime("%H:%M:%S")
st.caption(f"Kommune/region: {omraade} | Last updated: {danish_time}")
st.dataframe(df_grouped)
