#!/usr/bin python3
"""
This is the main file for the lambda project. It will be used in EC2 IAM role situation
"""
import os
import boto3
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

    Raises:
        db.exc.SQLAlchemyError: In case of any SQLAlchemy errors.
    """
    try:
        engine = db.create_engine(f'mysql+mysqlconnector://{user}:{password}@{database}.{host}:{port}/{schema}')
    except db.exc.SQLAlchemyError as err:
        raise err
    return engine


def get_data(engine: db.engine.base.Engine, sql: str) -> None:
    """
    This fucntion reads data from the database using the provided SQL query and save it as a JSON file.

    Args:
        engine (db.engine.base.Engine): SQLAlchemy engine.
        sql (str): SQL query to fetch data.

    Raises:
        pd.errors.PandasError: In case of any Pandas errors.
    """
    try:
        df = pd.read_sql(sql, con=engine)
        df[["customerID"]].head()
        df[["customerID"]].to_json('cus_id.json')
    except pd.errors.PandasError as err:
        raise err


def load_data(bucket: str, folder: str) -> None:
    """
    This function uploads the JSON file to the specified S3 bucket and folder.

    Args:
        bucket (str): S3 bucket name.
        folder (str): S3 folder.

    Raises:
        botocore.exceptions.BotoCoreError: In case of any Boto3 errors.
    """
    s3 = boto3.client('s3')
    file_path = 'cus_id.json'
    key = f'{folder}/cus_id.json'
    try:
        s3.upload_file(file_path, bucket, key)
    except botocore.exceptions.BotoCoreError as err:
        raise err
    

def main():
    app_config = toml.load('config_file.toml')

    host = app_config['db']['host']
    port = app_config['db']['port']
    database = app_config['db']['database']
    schema = app_config['db']['schema']

    bucket = app_config['s3']['bucket']
    folder = app_config['s3']['folder']

    load_dotenv()
    user = os.getenv('user')
    password = os.getenv('password')

    engine = mysql_connect(host, user, password, database, port, schema)

    get_data(engine, sql)

    load_data(bucket, folder)

if __name__ == "__main__":
    main()
