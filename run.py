#!/usr/bin python3
"""
This is the main file for the lambda project. It will be used in EC2 IAM role situation
"""
import os
import subprocess
from typing import Any
import pandas as pd
import sqlalchemy as db
import toml
from dotenv import load_dotenv

sql = """
    SELECT customerID, SUM(sales) sum_sales
    FROM orders
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10;
    """


def mysql_connect(host: str, user: str, password: str, database: str, port: str, schema: str) -> db.engine.base.Engine:
    """
    Connect to the MySQL database using provided credentials and schema.

    :param host: Database host.
    :param user: Database user.
    :param password: Database user password.
    :param database: Database name.
    :param port: Database port.
    :param schema: Database schema.
    :return: SQLAlchemy engine.
    """
    engine = db.create_engine(f'mysql+mysqlconnector://{user}:{password}@{database}.{host}:{port}/{schema}')
    return engine


def get_data(engine: db.engine.base.Engine, sql: str) -> None:
    """
    Read data from the database using the provided SQL query and save it as a JSON file.

    :param engine: SQLAlchemy engine.
    :param sql: SQL query to fetch data.
    """
    df = pd.read_sql(sql, con=engine)
    df[["customerID"]].head()
    df[["customerID"]].to_json('cus_id.json')


def load_data(bucket: str, folder: str) -> None:
    """
    Upload the JSON file to the specified S3 bucket and folder.

    :param bucket: S3 bucket name.
    :param folder: S3 folder.
    """
    s3 = boto3.client('s3')
    file_path = 'cus_id.json'
    key = f'{folder}/cus_id.json'
    s3.upload_file(file_path, bucket, key)
    

def main():
    app_config = toml.load('config_file.toml')

    host=app_config['db']['host']
    port=app_config['db']['port']
    database=app_config['db']['database']
    schema=app_config['db']['schema']

    bucket=app_config['s3']['bucket']
    folder=app_config['s3']['folder']

    load_dotenv()
    user=os.getenv('user')
    password=os.getenv('password')
    
    engine = mysql_connect(host, user, password, database, port,schema)

    get_data(engine, sql)

    load_data()

if __name__=="__main__": 
    main()



    

    