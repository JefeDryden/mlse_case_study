
import logging
import os
import json
import io

import pandas as pd
import boto3
import sqlalchemy 
import psycopg2
import requests

from sqlalchemy import create_engine
from datetime import date

#The code in this file performs Tasks 1-4 and Task 6. 
#Task 5 is completed using a Cloudwatch Event to trigger the Lambda daily.


#This uses today's date to create a filename for the raw data json
today = date.today().strftime("%y%m%d")
RAW_FILE_NAME = "raw_trending_json_"+today

#Saving the Database + Twitter info as an environment variable for security
POSTGRES_DB_NAME = os.environ.get("POSTGRES_DB_NAME")	
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")	
POSTGRES_TABLE = os.environ.get("POSTGRES_TABLE")	
POSTGRES_USER = os.environ.get("POSTGRES_USER")


BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
SEARCH_URL = "https://api.twitter.com/1.1/trends/place.json"

#Twitter uses a woeid for a location variable. For Canada it is 23424775
QUERY_PARAMS = {'id': '23424775'}

#Setting up logging for improved log visibility and error tracking
LOGGER = logging.getLogger(__name__)
if LOGGER.handlers:
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(name)-24s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
LOGGER.setLevel(logging.DEBUG)


#This function is used to authenticate myself for the Twitter API
def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "JefeDryden"
    
    return r


#This function connects to the Twitter API and retrieves the Trending Data (Task 1)
def connect_to_endpoint(url, params):
    LOGGER.info("started connect to endpoint")
    response = requests.get(url, auth=bearer_oauth, params=params)
    LOGGER.info(f"Twitter Reponse status code: {response.status_code}")
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
        
    return response.json()


#This function saves the raw data to an S3 storage bucket for historical purpose. (Task 2)
def save_json(twitter_json):
    LOGGER.info("Begin writing data to S3")
    s3 = boto3.resource('s3')
    s3object = s3.Object('mlserawdata', f'Canada/{RAW_FILE_NAME}.json')
    s3object.put(Body=(bytes(json.dumps(twitter_json).encode('UTF-8'))))
    LOGGER.info(f"Finished writing data to Canada/{RAW_FILE_NAME}.json")
    
  
#This function cleans the retrieved json file into a dataframe suitable for the SQL Table (Task 3 and 5)  
def cleanup(twitter_json):
    df = pd.json_normalize(twitter_json[0]['trends'])
    location = twitter_json[0]['locations'][0]['name']
    time_of_trends = twitter_json[0]['as_of']
    df.insert(0, 'trending_time', time_of_trends)
    df.insert(0, 'location', location)
    df.fillna({'tweet_volume':0}, inplace=True)
    LOGGER.info("Data cleaning completed")
    return df


#This function uploads the cleaned dataframe to the Postgres Server (Task 6)    
def upload_to_postgres(clean_df):
    engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}')
    clean_df.head(0).to_sql(POSTGRES_TABLE, engine, if_exists='append',index=False)
    
    LOGGER.info(f"Initializing connection with {POSTGRES_DB_NAME}") 
    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    clean_df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, POSTGRES_TABLE, null="") # null values become ''
    conn.commit()
    LOGGER.info(f"Finished uploading data to {POSTGRES_DB_NAME}")


def handler(event, context):
    json_response = connect_to_endpoint(SEARCH_URL, QUERY_PARAMS)
    LOGGER.info("Received data from Twitter")
    save_json(json_response)
    clean_df = cleanup(json_response)
    
    upload_to_postgres(clean_df)
