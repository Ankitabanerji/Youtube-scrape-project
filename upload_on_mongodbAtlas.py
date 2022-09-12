import base64
import pymongo
import os
import gridfs
import requests
import shutil
import logging
import re

# retrieving credentials from environment variable
creds = os.getenv('MONGO_CRED')
logging.basicConfig(level=logging.INFO)
client = pymongo.MongoClient(creds)

db1 = client['Youtube_data']
coll1 = db1['Users_comments_details']
coll2 = db1['thumbnail_image_details']


def upload_image_mongodb(file_name):
    with open(file_name, "rb") as image:
        image_string = base64.b64encode(image.read())

    fs = gridfs.GridFS(db1)
    put_image = fs.put(image_string)

    # delete image from local
    if os.path.isfile(file_name):
        os.remove(file_name)
        print(f"Image has been deleted: {file_name}")
        logging.info(f"Image has been deleted: {file_name}")
    else:
        print(f"Image does not exist: {file_name}")
        logging.info(f"Image does not exist: {file_name}")

    return put_image


def download_image(title, url):
    """Download image on local and upload on mongodb as base64 format"""
    file_name = "resources/images/" + re.sub('[^a-zA-Z0-9 \n]', '', title).replace(' ', '_') + ".jpeg"

    res = requests.get(url, stream=True)

    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        logging.info(f'Image successfully Downloaded: {file_name}')
    else:
        print("Image Couldn't be retrieved")

    return upload_image_mongodb(file_name)


def upload_on_mongodb(all_data):
    """Storing retrieved data on mongodb"""
    print("mongodb all_data", all_data)

    # Storing user comments details in table Users_comments_details
    for data in all_data['data']:
        d = {'Channel_name': data['Channel_name'], 'Video_title': data['Video_title'], 'User_comment_map': []}

        for user, comment in zip(data["Commenter's Name"], data['Comments']):
            d['User_comment_map'].append({user: comment})

        coll1.insert_one(d)
        print(f'uploaded {d}')
        logging.info(f'Users_comments_details : uploaded {d}')

    # Storing thumbnail image details in table thumbnail_image_details
    for data, thumbnail_list in zip(all_data["data"], all_data["thumbnail"]):
        print(data, thumbnail_list)
        obj_id = download_image(data['Video_title'], thumbnail_list)
        d2 = {'Channel_name': data['Channel_name'], 'Video_title': data['Video_title'], 'thumbnail_object_id': obj_id}
        coll2.insert_one(d2)
        logging.info(f'thumbnail_image_details : uploaded {d}')
