import snowflake.connector
from sqlalchemy import create_engine
import logging
import os
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Getting snowflake credentials from environment variable
user = os.getenv('USER')
passwrd = os.getenv('PASSWORD')
account_name = os.getenv('ACCOUNT')
warehouse_name = os.getenv('WAREHOUSE')
database_name = os.getenv('DATABASE')
schema_name = os.getenv('SCHEMA')


def execute_query(connection, query):
    db_cursor_eb = connection.cursor()
    db_cursor_eb.execute(query)
    db_cursor_eb.close()


def upload_on_snowflake(data):
    con_eb = snowflake.connector.connect(user=user,
                                         password=passwrd,
                                         account=account_name,
                                         warehouse=warehouse_name,
                                         database=database_name,
                                         schema=schema_name,
                                         autocommit=True)

    try:
        q = "create table if not exists youtubeData (id number autoincrement start 1 increment 1, Channel_name " \
            "varchar(100), " \
            "Video_title varchar(300), Num_Views varchar(15), Num_Likes varchar(15), " \
            "Num_Subscribers varchar(15), num_comments varchar(15), video_link varchar(200), Publish_Date varchar(50), " \
            "gdrive_link varchar(300)) "
        execute_query(con_eb, q)
        try:
            values = []
            for d in data['data']:
                d['Video_title'] = re.sub('[^a-zA-Z0-9 \n]', '', d['Video_title']).replace('\n', ' ')
                d['Channel_name'] = re.sub('[^a-zA-Z0-9 \n]', '', d['Channel_name']).replace('\n', ' ')

                val = (d['Channel_name'], d['Video_title'], d['Num Views'], d["Num Likes"]
                       , d["Num Subscribers"], d["Num Comments"], d["video_link"]
                       , d["Publish Date"], d["gdrive_link"])

                values.append(str(val))

            values = ",".join(values)
            insert_q = "insert into youtubeData (Channel_name, Video_title, Num_Views, Num_Likes, Num_Subscribers, " \
                       "num_comments, video_link, Publish_Date, gdrive_link)" \
                       " values " + str(values) + ";"
            execute_query(con_eb, insert_q)

        except Exception as e:
            logging.info(e)

    except Exception as e:
        logging.info(e)
