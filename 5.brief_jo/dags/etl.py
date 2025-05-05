from sqlalchemy import create_engine
import pandas as pd
import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import psycopg2
from airflow.sensors.python import PythonSensor
from airflow.sensors.filesystem import FileSensor


# Définition des chemins des fichiers
INPUT_CSV = "/opt/airflow/dags/data/fact_resultats_epreuves.csv"

def check_new_file():
    folder = "/opt/airflow/dags/data/"
    return any(f.endswith(".csv") for f in os.listdir(folder))

# Fonction d'extraction
def extract_data():
    df = pd.read_csv(INPUT_CSV, sep=',')
    print(f"✅ Données extraites : {df.shape[0]} lignes")
    return df.to_json()  

def load_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract_task')
    df = pd.read_json(data)

    engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres:5432/airflow')

    with engine.connect() as conn:
        # Charger les ID déjà en base
        existing_ids = pd.read_sql("SELECT id_resultat FROM table_jo", conn)
        
        # Filtrer les nouvelles lignes
        df_new = df[~df['id_resultat'].isin(existing_ids['id_resultat'])]
        
        if df_new.empty:
            print("✅ Aucune nouvelle ligne à insérer.")
        else:
            df_new.to_sql('table_jo', conn, if_exists='append', index=False)
            print(f"✅ {len(df_new)} nouvelles lignes insérées.")

# Définition du DAG
dag = DAG(
    'csv_etl_pipeline',
    description         = 'Pipeline ETL pour extraire et charger des données CSV dans une base de données PostgreSQL',
    schedule_interval   = '0 * * * *',
    start_date          = datetime(2025, 5, 5),
    catchup             = False
)

extract_task = PythonOperator(task_id='extract_task', python_callable=extract_data, dag=dag)
# transform_task = PythonOperator(task_id='transform_task', python_callable=transform_data, provide_context=True, dag=dag)
load_task = PythonOperator(task_id='load_task', python_callable=load_data, provide_context=True, dag=dag)


extract_task >> load_task

