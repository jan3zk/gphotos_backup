import os
import numpy as np
import pickle
from glob import glob
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import requests
import piexif
import piexif.helper
import argparse
from pathlib import Path
import logging
from PIL.PngImagePlugin import PngImageFile, PngInfo
import collections
from dateutil import parser
import time


pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_colwidth', 150)
pd.set_option('display.width', 150)
pd.set_option('expand_frame_repr', True)

def download_file(url:str, destination_folder:str, file_name:str):
  response = requests.get(url)
  if response.status_code == 200:
    with open(os.path.join(destination_folder, file_name), 'wb') as f:
      f.write(response.content)
      f.close()

def gphotos_backup():
  credentialsFile = glob('*.json')[0]
  pickleFile = 'token.pickle'
  SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
  creds = None
  if os.path.exists(pickleFile):
    with open(pickleFile, 'rb') as token:
      creds = pickle.load(token)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        credentialsFile, SCOPES)
      creds = flow.run_local_server()
    with open(pickleFile, 'wb') as token:
      pickle.dump(creds, token)
  service = build('photoslibrary', 'v1', credentials=creds, cache_discovery=False, static_discovery=False)

  # Get all album names
  nextpagetoken = 'Dummy'
  myAlbums_list = []
  while nextpagetoken != '':
    nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
    myAlbums = service.albums().list(pageSize=10,pageToken=nextpagetoken).execute()
    myAlbums_list.append(pd.DataFrame(myAlbums.get('albums')))
    nextpagetoken = myAlbums.get('nextPageToken', '')
  dfAlbums = pd.concat(myAlbums_list).reset_index(drop=True)
  if args.albums[0] == 'all':
    album_titles = dfAlbums['title']
  else:
    album_titles = args.albums

  # Backup albums one by one
  for album_idx, album_title in enumerate(album_titles):
    print('\nBacking-up album %s (%d/%d) ...'%(album_title, album_idx+1, len(album_titles)))
    if not dfAlbums[dfAlbums['title'] == album_title]['id'].empty:
      album_id = dfAlbums[dfAlbums['title'] == album_title]['id'].to_string(index=False).strip()
    else:
      print('Wrong album name.')
      return
    album_dir = os.path.join(args.dir,album_title)
    Path(album_dir).mkdir(parents=True, exist_ok=True)
    nextpagetoken = 'Dummy'
    img_idx = 1
    file_names = []
    f_cap = open(os.path.join(album_dir,'captions.csv'),'w')
    while nextpagetoken != '':
      nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
      results = service.mediaItems().search(body={'albumId': album_id, 'pageToken': nextpagetoken}).execute()
      media_files = results.get('mediaItems', [])  
      nextpagetoken = results.get('nextPageToken', '')
      for media_file in media_files:
        file_name = media_file['filename']
        file_names.append(file_name)
        img_path = os.path.join(album_dir, file_name)
        _, img_ext = os.path.splitext(img_path)
        if img_ext in ['.avi','.AVI','.mp4','.MP4','.mov','.MOV','.vmw','.VMW']:
          download_url = media_file['baseUrl'] + '=dv'
        else:
          download_url = media_file['baseUrl'] + '=d'

        # Download image if it doesn't already exist locally
        if not os.path.isfile(img_path):
          dl_count = 0
          while dl_count < 3:
            try:
              print('Downloading file %s (%d).'%(file_name, img_idx), end='')
              download_file(download_url, album_dir, file_name)
            except:
              dl_count = dl_count + 1
              logging.exception('Connection error ...')
            else:
              break
        else:
          print('Skip downloading file %s (%d).'%(file_name, img_idx), end='')

        # Embed description into image metadata
        if 'description' in media_file:
          user_comment = media_file['description']
          print(' Description: %s'%user_comment)
          if img_ext in ['.jpg','.JPG','.jpeg','.JPEG','.tiff','.TIFF','.tif','.TIF']:
            exif_dict = piexif.load(img_path)
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = bytes(user_comment, "utf-8")
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(user_comment,encoding='unicode')#unicode
            exif_bytes = piexif.dump(exif_dict) 
            piexif.insert(exif_bytes, img_path)
          elif img_ext in ['.png','.PNG']:
            targetImage = PngImageFile(img_path)
            metadata = PngInfo()
            metadata.add_text("User Comment", user_comment)
            targetImage.save(img_path, pnginfo=metadata)

        else:
          print(' Without description.')
          user_comment = '' # insert an empty string into the User Comment Exif field to erase <data too large to display>
          if img_ext in ['.jpg','.JPG','.jpeg','.JPEG','.tiff','.TIFF','.tif','.TIF']:
            exif_dict = piexif.load(img_path)
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = bytes(user_comment, "utf-8")
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(user_comment,encoding='unicode')
            exif_bytes = piexif.dump(exif_dict) 
            piexif.insert(exif_bytes, img_path)

        # Change file modification date
        creation_time = media_file['mediaMetadata']['creationTime']
        creation_time_dt = parser.parse(creation_time)
        if img_ext in ['.jpg','.JPG','.jpeg','.JPEG','.tiff','.TIFF','.tif','.TIF']:
          exif_dict = piexif.load(img_path)
          exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = creation_time_dt.strftime('%d/%m/%Y %H:%M')
          exif_bytes = piexif.dump(exif_dict)
          piexif.insert(exif_bytes, img_path)
        access_time = time.mktime(creation_time_dt.timetuple())
        modified_time = access_time
        os.utime(img_path,(access_time, modified_time))
        img_idx = img_idx + 1

        f_cap.write(file_name+'\t'+user_comment+'\n')

    f_cap.close()

    # Check for duplicates
    duplicates = [item for item, count in collections.Counter(file_names).items() if count > 1]
    if duplicates:
      print('Photos with duplicated file names that were not copied: ')
      print(*duplicates, sep=', ')

    # Check for photos that are missing on the server side
    for _, _, lfiles in os.walk(album_dir):
      local_files = [f for f in lfiles if not f.endswith('.csv')]
    not_on_server = np.setdiff1d(local_files ,file_names)
    if not_on_server.size > 0:
      print('\nFiles that do not exist on the server:')
      for local_file in not_on_server:
        print(local_file)


if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('-a', '--albums',
    type = str,
    nargs = '+',
    default = ['all'],
    help = "A list of album names to backup. Backup everything if set to 'all'.")
  ap.add_argument('-d', '--dir',
    type = str,
    default = os.path.expanduser('~/Pictures'),
    help = "The directory where album folders are downloaded.")
  args = ap.parse_args()
  gphotos_backup()
