import streamlit as st
import pandas as pd
import time
from databricks import sql
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from zoneinfo import ZoneInfo

SERVER_HOST = st.secrets["SERVER_HOST"]
HTTP_PATH = st.secrets["HTTP_PATH"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]

st.set_page_config(page_title="SFU Kandidater", layout="wide")
st.title("Personlige stemmer 2025 - SFU kandidater")

# query = """
# SELECT kandidat as Kandidat,
#        antal_stemmer as `Antal stemmer`
# FROM workspace.valgresultat.personlige_stemmer_krv_2025
# WHERE SFU_kandidat = 'Ja'
# ORDER BY kandidat;
# """

# with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
#     with c.cursor() as cur:
#         cur.execute(query)
#         df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])

url = "https://raw.githubusercontent.com/Kolupso/valgresultater_KRV_2025/refs/heads/main/combined_results.csv"
df = pd.read_csv(url)
df["antal_stemmer"] = df["antal_stemmer"].astype(int)

df_sfu = (
    df[df["SFU_kandidat"] == "Ja"]     # WHERE SFU_kandidat = 'Ja'
      .loc[:, ["kandidat", "antal_stemmer"]]   # SELECT columns
      .rename(columns={
          "kandidat": "Kandidat",
          "antal_stemmer": "Antal stemmer"
      })
      .sort_values("Kandidat")          # ORDER BY kandidat
      .reset_index(drop=True)
)


st_autorefresh(interval=30_000)
st.dataframe(df_sfu)
danish_time = datetime.now(ZoneInfo("Europe/Copenhagen")).strftime("%H:%M:%S")
st.caption(f"Last updated: {danish_time}")
