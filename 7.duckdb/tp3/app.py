import streamlit as st
import pandas as pd
import numpy as np
import duckdb as dd
import plotly.express as px


st.title("App DuckDB")

duckdb_conn_tp1 = dd.connect(
    "../data/jeux_olympiques.duckdb", 
    read_only=False
)

duckdb_conn_tp2 = dd.connect(
    "../data/weather_data.duckdb", 
    read_only=False
)

st.subheader('TP1: Jeux Olympiques')
query = st.text_area("Entrez votre requête SQL :", "SELECT * FROM resultats")
df_tp1 = duckdb_conn_tp1.execute(query).fetchdf()
# Bouton exécution
if st.button("Exécuter la requête"):
    try:
        # Lecture SQL
        df_tp1 = duckdb_conn_tp1.execute(query).fetchdf()
        st.success(f"Requête exécutée. {len(df_tp1)} lignes retournées.")
        st.dataframe(df_tp1)
    except Exception as e:
        st.error(f"Erreur : {e}")

st.subheader('TP2: Weather Data')
query_2 = st.text_area("Entrez votre requête SQL :", "SELECT * FROM weather_data LIMIT 10")
if st.button("Exécuter la requête", key="tp2"):
    try:
        # Lecture SQL
        df_tp2 = duckdb_conn_tp2.execute("SELECT * FROM weather_data").fetchdf()
        st.success(f"Requête exécutée. {len(df_tp2)} lignes retournées.")
        st.dataframe(df_tp2)
    except Exception as e:
        st.error(f"Erreur : {e}")
        
        
# Create separator
st.markdown("---")
st.subheader("Nombre de fois que le pays est arrivé à chaque place")
pays = st.selectbox("Choisir un pays", sorted(df_tp1["pays_en_base_resultats"].dropna().unique()))
df_tp1_filtre = df_tp1[df_tp1["pays_en_base_resultats"] == pays]
df_tp1_filtre["classement_epreuve"] = pd.to_numeric(df_tp1_filtre["classement_epreuve"], errors="coerce").astype("Int64")
place_counts = df_tp1_filtre["classement_epreuve"].value_counts().sort_index()

st.bar_chart(place_counts.sort_index())

st.markdown("---")
gold_df = df_tp1[df_tp1["classement_epreuve"] == "1"]
# Compter les médailles d'or par pays
gold_count = gold_df["pays_en_base_resultats"].value_counts().reset_index()
gold_count.columns = ["country", "gold_medals"]


fig = px.choropleth(
    gold_count,
    locations="country",
    locationmode="country names", 
    color="gold_medals",
    color_continuous_scale="YlOrBr",
    title="Pays avec le plus de médailles d'or",
)

st.plotly_chart(fig, use_container_width=True)