import os
import json
import toml
import requests
import pandas as pd
import sqlalchemy as db
from typing import Tuple
from dotenv import load_dotenv
from datetime import date
import boto3

def mysql_connect(host: str, 
                  user: str, 
                  password: str, 
                  database: str, 
                  port: str, 
                  schema: str) -> db.engine.base.Engine:
    """
    This function connects to the MySQL database using provided credentials and schema.

    Args:
        host (str): Database host.
        user (str): Database user.
        password (str): Database user password.
        database (str): Database name.
        port (str): Database port.
        schema (str): Database schema.

    Returns:
        db.engine.base.Engine: SQLAlchemy engine.
    """
    try:
        engine = db.create_engine(f'mysql+mysqlconnector://{user}:{password}@{database}.{host}:{port}/{schema}')
        return engine
    except Exception as err:
        raise ValueError(f"Database connection failed: {err}")

def get_customer_id(cusid_file: str) -> str:
    """
    This funtion reads customer_id_file and return a string list of customer_id.

    Args:
        cusid_file (str): File path of the JSON file containing customer IDs.

    Returns:
        str: A string containing comma-separated customer IDs.
    """
    try:
        with open(cusid_file, 'rb') as f:
            data = json.load(f)
        customer_ids = [str(value) for value in data["customerID"].values()]
        id_string = f"({','.join(customer_ids)})"
        return id_string
    except Exception as err:
        raise ValueError(f"Failed to read customer ID file: {err}")

def get_customer_data(engine: db.engine.base.Engine, sql: str) -> str:
    """
    This function gets customer data from the database.

    Args:
        engine (db.engine.base.Engine): SQLAlchemy engine.
        sql (str): SQL query to fetch customer data.

    Returns:
        str: JSON-formatted customer data.
    """
    try:
        mysql_result = engine.execute(sql)
        records = [
            {"id": row[0], "name": row[1], "date": date.today().strftime("%Y-%m-%d")}
            for row in mysql_result
        ]
        return records
    except Exception as err:
        raise ValueError(f"Failed to fetch customer data: {err}")

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    app_config = toml.load("config.toml")
    api_url = app_config["api"]["api_url"]

    host = app_config["db"]["host"]
    port = app_config["db"]["port"]
    database = app_config["db"]["database"]
    schema = app_config["db"]["schema"]

    load_dotenv()
    user = os.getenv("user")
    password = os.getenv("password")

    s3_client = boto3.client("s3")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"].split("/")[1]

    filepath = "/tmp/" + key
    download_key = "input/" + key

    s3_client.download_file(Bucket=bucket, Key=download_key, Filename=filepath)

    try:
        engine = mysql_connect(host, user, password, database, port, schema)
        ids = get_customer_id(filepath)

        sql = f"""SELECT customerID, CustomerName
                  FROM customers
                  WHERE customerID in {ids};
               """
        records = get_customer_data(engine, sql)

        headers = {'Content-Type': 'application/json'}

        response = requests.post(api_url, json=records, headers=headers)
        print(response.status_code)
        return response.status_code

    except Exception as err:
        print(f"Error: {err}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(err)})
        }
