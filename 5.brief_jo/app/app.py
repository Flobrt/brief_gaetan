import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Connexion à PostgreSQL
@st.cache_resource
def get_engine():
    return create_engine('postgresql+psycopg2://airflow:airflow@postgres:5432/airflow')  # adapte si nécessaire

# Titre
st.title("🔎 Requête SQL PostgreSQL")

# Zone de saisie SQL
query = st.text_area("💬 Entrez votre requête SQL :", "SELECT * FROM table_jo LIMIT 10")

# Bouton exécution
if st.button("Exécuter la requête"):
    try:
        # Lecture SQL
        df = pd.read_sql(query, get_engine())
        st.success(f"✅ Requête exécutée. {len(df)} lignes retournées.")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        
        
    # Bouton de téléchargement
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Télécharger les résultats au format CSV",
        data=csv,
        file_name="resultats_requete.csv",
        mime="text/csv"
        )
