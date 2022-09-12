from upload_on_mongodbAtlas import upload_on_mongodb
from snowflake_connect import upload_on_snowflake
from download_store_video_gdrive import download_video
import logging

logging.basicConfig(level=logging.DEBUG)


def upload_operations(alldata):
    idx = 0

    try:
        # downloading and uploading video on Google Drive and retrieving the drive link
        logging.info("started uploading on gdrive")
        while idx < len(alldata['data']):
            gdrive_link = download_video(alldata['data'][idx]['video_link'], alldata['data'][idx]['Video_title'])
            alldata['data'][idx]['gdrive_link'] = gdrive_link
            idx += 1
        logging.info("done uploading on gdrive")
    except Exception as e:
        logging.info(e)

    # storing data on mongodb(thumbnail images and commenter's details)
    logging.info("started uploading on mongodb")
    upload_on_mongodb(alldata)
    logging.info("done uploading on mongodb")

    # storing data on snowflake database table
    logging.info("started uploading on snowflake")
    upload_on_snowflake(alldata)
    logging.info("done uploading on snowflake")
