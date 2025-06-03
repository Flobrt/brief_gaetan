import duckdb
import os


# Vider le dossier de sortie s'il existe déjà
output_dir = "../outputs"
if os.path.exists(output_dir):
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {file_path}: {e}")

# Connexion à une base DuckDB
con = duckdb.connect("../data/jeux_olympiques.duckdb")

# Lire le CSV et l'écrire en Parquet
con.execute("""
    COPY (
        SELECT * FROM read_csv_auto('data/fact_resultats_epreuves.csv')
    ) TO '../outputs/jeux_olympiques.parquet' (FORMAT 'parquet');
""")

print("Conversion terminée : CSV → Parquet")

csv_path = "data/fact_resultats_epreuves.csv"
parquet_path = "../outputs/jeux_olympiques.parquet"

# Création d'une table DuckDB à partir du fichier Parquet
con.execute("DROP TABLE IF EXISTS resultats")
con.execute(f"""
    CREATE TABLE resultats AS
    SELECT * FROM parquet_scan('{parquet_path}')
""")

# Sélection des données du fichier CSV
con.execute("PRAGMA profiling_mode='standard'")
con.execute("PRAGMA profiling_output='../outputs/1.profiling_csv_select.txt'")
con.execute("PRAGMA enable_profiling")
con.execute(f"SELECT * FROM read_csv_auto('{csv_path}')").fetchdf()

# Seelction des données du fichier Parquet
con.execute("PRAGMA profiling_mode='standard'")
con.execute("PRAGMA profiling_output='../outputs/1.profiling_parquet_select.txt'")
con.execute("PRAGMA enable_profiling")
con.execute(f"SELECT * FROM parquet_scan('{parquet_path}')").fetchdf()

print("Comparaison terminée select : CSV vs Parquet")

# Comparaison des performances d'aggrégation
con.execute("PRAGMA profiling_mode='standard'")
con.execute("PRAGMA profiling_output='../outputs/2.profiling_csv_aggregation.txt'")
con.execute("PRAGMA enable_profiling")
con.execute(f"""
    SELECT 
        id_pays,
        COUNT(*) AS total_podiums
    FROM read_csv_auto('{csv_path}')
    GROUP BY id_pays
    ORDER BY total_podiums DESC
    LIMIT 10
""").fetchdf()

# Comparaison des performances d'aggrégation
con.execute("PRAGMA profiling_mode='standard'")
con.execute("PRAGMA profiling_output='../outputs/2.profiling_parquet_aggregation.txt'")
con.execute("PRAGMA enable_profiling")
con.execute(f"""
    SELECT 
        id_pays,
        COUNT(*) AS total_podiums
    FROM parquet_scan('{parquet_path}')
    GROUP BY id_pays
    ORDER BY total_podiums DESC
    LIMIT 10
""").fetchdf()

# Comparaison des performances d'aggrégation 
con.execute("PRAGMA profiling_mode='standard'")
con.execute("PRAGMA profiling_output='../outputs/2.profiling_db_aggregation.txt'")
con.execute("PRAGMA enable_profiling")
con.execute("""
    SELECT 
        id_pays,
        COUNT(*) AS total_podiums
    FROM resultats
    GROUP BY id_pays
    ORDER BY total_podiums DESC
    LIMIT 10
""").fetchdf()

print("Comparaison terminée agrégation : CSV vs Parquet vs DB")

# Fermeture de la connexion
con.close()
print("Connexion à DuckDB fermée")