from pytube import YouTube
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import os
import re
import logging

logging.basicConfig(level=logging.INFO)

# Getting google cloud api service account credentials from environment variable
service_account_info = json.loads(os.getenv('CREDENTIALS'))
creds = service_account.Credentials.from_service_account_info(
    service_account_info)


def upload_video_googledrive(v_title):
    """Using google cloud api service account to store downloaded video on gdrive and returning downloaded video
    gdrive link """
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': v_title + '.mp4',
                         "parents": ["1_gwj96gYxHsmvkr9u0MR_4iQrp1PHzLg"]}
        media = MediaFileUpload('./resources/' + v_title, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(f"{v_title} uploaded successfully on drive id: {file.get('id')}")
        logging.info(f"{v_title} uploaded successfully on drive id: {file.get('id')}")

    except HttpError as error:
        print(f'An error occurred: {error}')
        logging.info(f'An error occurred: {error}')
        file = None

    return "https://drive.google.com/file/d/" + file.get('id') + "/view?usp=sharing"


def download_video(v_link, v_title):
    yt = YouTube(v_link)
    try:
        file_name = re.sub('[^a-zA-Z0-9 \n]', '', v_title).replace(' ', '_')
        yt.streams.filter(progressive=True,
                          file_extension="mp4").first().download(output_path="resources/",
                                                                 filename=file_name)
        print("file_name= ", file_name)
        print(f"{v_link} downloaded successfully in local")
        try:
            fid = upload_video_googledrive(file_name)

            file_path = 'resources/' + file_name
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File has been deleted: {file_name}")
            else:
                print(f"File does not exist: {file_name}")
            return fid

        except Exception as e:
            print(f"could not upload: {e}, link: {v_link}, title: {v_title}")

    except Exception as e:
        print(f"{v_link} could not be downloaded in local.ERROR: {e}")



