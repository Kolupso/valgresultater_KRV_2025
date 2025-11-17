import streamlit as st
import pandas as pd
import time
from databricks import sql
from streamlit_autorefresh import st_autorefresh

# ---- Connection Settings ----
SERVER_HOST = st.secrets["SERVER_HOST"]
HTTP_PATH = st.secrets["HTTP_PATH"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]




# valg = st.sidebar.selectbox("Vælg valg", ["Kommunalvalg", "Regionsrådsvalg"])

omraade = st.sidebar.selectbox("Vælg kommune/region", [
    "Albertslund Kommune",
    "Allerød Kommune",
    "Assens Kommune",
    "Ballerup Kommune",
    "Billund Kommune",
    "Bornholms Regionskommune",
    "Brøndby Kommune",
    "Brønderslev Kommune",
    "Dragør Kommune",
    "Egedal Kommune",
    "Esbjerg Kommune",
    "Fanø Kommune",
    "Favrskov Kommune",
    "Faxe Kommune",
    "Fredensborg Kommune",
    "Fredericia Kommune",
    "Frederiksberg Kommune",
    "Frederikshavn Kommune",
    "Frederikssund Kommune",
    "Furesø Kommune",
    "Faaborg-Midtfyn Kommune",
    "Gentofte Kommune",
    "Gladsaxe Kommune",
    "Glostrup Kommune",
    "Greve Kommune",
    "Gribskov Kommune",
    "Guldborgsund Kommune",
    "Haderslev Kommune",
    "Halsnæs Kommune",
    "Hedensted Kommune",
    "Helsingør Kommune",
    "Herlev Kommune",
    "Herning Kommune",
    "Hillerød Kommune",
    "Hjørring Kommune",
    "Holbæk Kommune",
    "Holstebro Kommune",
    "Horsens Kommune",
    "Hvidovre Kommune",
    "Høje-Taastrup Kommune",
    "Hørsholm Kommune",
    "Ikast-Brande Kommune",
    "Ishøj Kommune",
    "Jammerbugt Kommune",
    "Kalundborg Kommune",
    "Kerteminde Kommune",
    "Kolding Kommune",
    "Københavns Kommune",
    "Køge Kommune",
    "Langeland Kommune",
    "Lejre Kommune",
    "Lemvig Kommune",
    "Lolland Kommune",
    "Lyngby-Taarbæk Kommune",
    "Læsø Kommune",
    "Mariagerfjord Kommune",
    "Middelfart Kommune",
    "Morsø Kommune",
    "Norddjurs Kommune",
    "Nordfyns Kommune",
    "Nyborg Kommune",
    "Næstved Kommune",
    "Odder Kommune",
    "Odense Kommune",
    "Odsherred Kommune",
    "Randers Kommune",
    "Rebild Kommune",
    "Ringkøbing-Skjern Kommune",
    "Ringsted Kommune",
    "Roskilde Kommune",
    "Rudersdal Kommune",
    "Rødovre Kommune",
    "Samsø Kommune",
    "Silkeborg Kommune",
    "Skanderborg Kommune",
    "Skive Kommune",
    "Slagelse Kommune",
    "Solrød Kommune",
    "Sorø Kommune",
    "Stevns Kommune",
    "Struer Kommune",
    "Svendborg Kommune",
    "Syddjurs Kommune",
    "Sønderborg Kommune",
    "Thisted Kommune",
    "Tønder Kommune",
    "Tårnby Kommune",
    "Vallensbæk Kommune",
    "Varde Kommune",
    "Vejen Kommune",
    "Vejle Kommune",
    "Vesthimmerlands Kommune",
    "Viborg Kommune",
    "Vordingborg Kommune",
    "Ærø Kommune",
    "Aabenraa Kommune",
    "Aalborg Kommune",
    "Aarhus Kommune",
    "Region Nordjylland",
    "Region Syddanmark",
    "Region Midtjylland",
    "Region Østdanmark"
])

query = f"SELECT * FROM workspace.valgresultat.personlige_stemmer_krv_2025 WHERE `kommune/region` = '{omraade}' AND kandidat != 'Listestemmer' ORDER BY parti, kandidat"
overblik_query = f"SELECT parti, sum(antal_stemmer) FROM workspace.valgresultat.personlige_stemmer_krv_2025 WHERE `kommune/region` = '{omraade}' GROUP BY parti"


kommunalvalg_query = "SELECT * FROM workspace.valgresultat.personlige_stemmer_kv_2025"
regionvalg_query = "SELECT * FROM workspace.valgresultat.personlige_stemmer_rv_2025"

page_dict = {"Kommunalvalg": kommunalvalg_query, "Regionsrådsvalg": regionvalg_query}

# # Page selector
# table = st.sidebar.selectbox("Vælg tabel", ["Kommunalvalg", "Regionsrådsvalg"])

# table_query = page_dict[f"{table}"]

st_autorefresh(interval=30_000, key=omraade)

with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
    with c.cursor() as cur:
        cur.execute(f"{query}")
        df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])

with sql.connect(server_hostname=SERVER_HOST, http_path=HTTP_PATH, access_token=ACCESS_TOKEN) as c:
    with c.cursor() as cur2:
        cur2.execute(f"{overblik_query}")
        df_overblik = pd.DataFrame(cur2.fetchall(), columns=[d[0] for d in cur.description])



st.set_page_config(page_title="Databricks Dashboard", layout="wide")
st.title(f"Personlige stemmer 2025 - {omraade}")

st.dataframe(df)
st.caption(f"Kommune/region: {omraade} | Last updated: {time.strftime('%H:%M:%S')}")

st.dataframe(df_overblik)


# streamlit run databricks_live_dashboard.py
