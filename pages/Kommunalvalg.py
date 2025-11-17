import streamlit as st
import pandas as pd
import time
from databricks import sql
from streamlit_autorefresh import st_autorefresh

# ---- Connection Settings ----
SERVER_HOST = st.secrets["SERVER_HOST"]
HTTP_PATH = st.secrets["HTTP_PATH"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]

st.set_page_config(page_title="Kommuner", layout="wide")
st.title("Personlige stemmer 2025 - Kommuner")

# Select region
omraade = st.sidebar.selectbox("Vælg kommune/region", [
    "Albertslund Kommune", "Allerød Kommune", "Assens Kommune", "Ballerup Kommune", "Billund Kommune",
    "Bornholms Regionskommune", "Brøndby Kommune", "Brønderslev Kommune", "Dragør Kommune",
    "Egedal Kommune", "Esbjerg Kommune", "Fanø Kommune", "Favrskov Kommune", "Faxe Kommune",
    "Fredensborg Kommune", "Fredericia Kommune", "Frederiksberg Kommune", "Frederikshavn Kommune",
    "Frederikssund Kommune", "Furesø Kommune", "Faaborg-Midtfyn Kommune", "Gentofte Kommune",
    "Gladsaxe Kommune", "Glostrup Kommune", "Greve Kommune", "Gribskov Kommune", "Guldborgsund Kommune",
    "Haderslev Kommune", "Halsnæs Kommune", "Hedensted Kommune", "Helsingør Kommune", "Herlev Kommune",
    "Herning Kommune", "Hillerød Kommune", "Hjørring Kommune", "Holbæk Kommune", "Holstebro Kommune",
    "Horsens Kommune", "Hvidovre Kommune", "Høje-Taastrup Kommune", "Hørsholm Kommune",
    "Ikast-Brande Kommune", "Ishøj Kommune", "Jammerbugt Kommune", "Kalundborg Kommune",
    "Kerteminde Kommune", "Kolding Kommune", "Københavns Kommune", "Køge Kommune", "Langeland Kommune",
    "Lejre Kommune", "Lemvig Kommune", "Lolland Kommune", "Lyngby-Taarbæk Kommune", "Læsø Kommune",
    "Mariagerfjord Kommune", "Middelfart Kommune", "Morsø Kommune", "Norddjurs Kommune", "Nordfyns Kommune",
    "Nyborg Kommune", "Næstved Kommune", "Odder Kommune", "Odense Kommune", "Odsherred Kommune",
    "Randers Kommune", "Rebild Kommune", "Ringkøbing-Skjern Kommune", "Ringsted Kommune",
    "Roskilde Kommune", "Rudersdal Kommune", "Rødovre Kommune", "Samsø Kommune", "Silkeborg Kommune",
    "Skanderborg Kommune", "Skive Kommune", "Slagelse Kommune", "Solrød Kommune", "Sorø Kommune",
    "Stevns Kommune", "Struer Kommune", "Svendborg Kommune", "Syddjurs Kommune", "Sønderborg Kommune",
    "Thisted Kommune", "Tønder Kommune", "Tårnby Kommune", "Vallensbæk Kommune", "Varde Kommune",
    "Vejen Kommune", "Vejle Kommune", "Vesthimmerlands Kommune", "Viborg Kommune", "Vordingborg Kommune",
    "Ærø Kommune", "Aabenraa Kommune", "Aalborg Kommune", "Aarhus Kommune"
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
AND `kommune/region` not like '%Region%'
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
AND `kommune/region` not like '%Region%'
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
