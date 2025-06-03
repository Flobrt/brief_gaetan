import requests 
import pandas as pd
import duckdb as dd
import logging
# import json

print('ok')
# Set up logging
logging.basicConfig(
    filename    = "../data/weather_data.log",
    level       = logging.INFO, 
    format      = '%(asctime)s - %(levelname)s - %(message)s'
)

city    = "Lyon"
api_key = "24fb1fbeb97ffecbdf8a28facb1898f0"

url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'.format(city, api_key)

# Attempt to make a request to the OpenWeatherMap API
try:
    res = requests.get(url)
    logging.info(f"Request to {url} successful.")
except requests.exceptions.RequestException as e:
    logging.error(f"Request to {url} failed: {e}")
    raise

# Check if the request was successful
try:
    data = res.json()
    logging.info("JSON data retrieved successfully.")
except ValueError as e:
    logging.error(f"Failed to parse JSON data: {e}")
    raise

# Convert the json data to a pandas DataFrame
try:
    df = pd.json_normalize(data)
    logging.info("JSON data converted to DataFrame successfully.")
except Exception as e:
    logging.error(f"Failed to convert JSON data to DataFrame: {e}")
    raise

# Drop null values
try:
    df = df.dropna()
    logging.info("Null values dropped from DataFrame.")
except Exception as e:
    logging.error(f"Failed to drop null values from DataFrame: {e}")
    raise

# Drop columns
try:
    df = df.drop(columns=['wind.gust', 'clouds.all', 'sys.type', 'sys.id',])
    logging.info("Unnecessary columns dropped from DataFrame.")
except KeyError as e:
    logging.error(f"Failed to drop columns from DataFrame: {e}")
    raise


# Convert the DataFrame to a DuckDB table
try:
    con = dd.connect(database='../data/weather_data.duckdb', read_only=False)
    con.execute("CREATE TABLE IF NOT EXISTS weather_data AS SELECT * FROM df")
    logging.info("DuckDB connection established and table created.")
except Exception as e:
    logging.error(f"Failed to connect to DuckDB or create table: {e}")
    raise

# Save the DataFrame to a DuckDB table
try:
    con.execute("INSERT INTO weather_data SELECT * FROM df")
    logging.info("DataFrame saved to DuckDB table successfully.")
except Exception as e:
    logging.error(f"Failed to save DataFrame to DuckDB table: {e}")
    raise

# Save the Dataframe to parquet file
try:
    df.to_parquet('../data/weather_data.parquet', index=False)
    logging.info("DataFrame saved to Parquet file successfully.")
except Exception as e:
    logging.error(f"Failed to save DataFrame to Parquet file: {e}")
    raise

# Save the json data to a file
# with open('../data/weather_data.json', 'w') as f:
#     json.dump(data, f, indent=4)