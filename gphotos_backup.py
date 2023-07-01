import os, sys
import pickle
import argparse
from glob import glob
from pathlib import Path
import logging
import collections
from dateutil import parser
import time

import numpy as np
import pandas as pd
import requests
import piexif
import piexif.helper
from PIL.PngImagePlugin import PngImageFile, PngInfo
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Constants
IMG_EXTS = ['.jpg', '.jpeg', '.tiff', '.tif']
VID_EXTS = ['.avi', '.mp4', '.mov', '.vmw']
PNG_EXTS = ['.png']
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

def save_metadata(file_path, user_comment, creation_time_dt, file_ext) -> None:
  if file_ext.lower() in IMG_EXTS:
    # EXIF user comment
    exif_dict = piexif.load(file_path)
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = bytes(user_comment, "utf-8")
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(user_comment, encoding='unicode')
    # EXIF modification date
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = creation_time_dt.strftime('%d/%m/%Y %H:%M')
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_path)
  elif file_ext.lower() in PNG_EXTS:
    # PngInfo User comment
    targetImage = PngImageFile(file_path)
    metadata = PngInfo()
    metadata.add_text("User Comment", user_comment)
    targetImage.save(file_path, pnginfo=metadata)
  # File modification date
  os.utime(file_path,(time.mktime(creation_time_dt.timetuple()),) * 2)

def download_file(url: str, destination: Path) -> None:
  response = requests.get(url)
  response.raise_for_status()  # raise an exception if a non-success status code is returned
  destination.write_bytes(response.content)

def authenticate_google_photos():
  credentials_file = next(Path.cwd().glob('*.json'))
  pickle_file = Path.cwd() / 'token.pickle'
  #scopes = ['https://www.googleapis.com/auth/photoslibrary.readonly']
  creds = None
  if os.path.exists(pickle_file):
    with open(pickle_file, 'rb') as token:
      creds = pickle.load(token)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
      creds = flow.run_local_server()
    with open(pickle_file, 'wb') as token:
        pickle.dump(creds, token)
  return creds

def get_album_ids_and_names(srv):
  ids_names = []
  request = srv.albums().list()
  while request is not None:
      response = request.execute()
      albums = response.get('albums', [])
      for album in albums:
          ids_names.append((album['id'], album['title']))
      request = srv.albums().list_next(request, response)
  return ids_names

def gphotos_backup(work_dir, albums, max_retries):
  creds = authenticate_google_photos()
  service = build('photoslibrary', 'v1', credentials=creds, cache_discovery=False, static_discovery=False)

  albums_in = get_album_ids_and_names(service)
  album_titles = [item[1] for item in albums_in] if albums[0] == 'all' else albums

  for album_idx, album_title in enumerate(album_titles):
    album_id = [item[0] for item in albums_in if item[1] == album_title][0]
    album_dir = Path(work_dir) / album_title
    print(f'\nBacking-up album {album_title} ({album_idx+1}/{len(album_titles)}) ...')
    album_dir.mkdir(parents=True, exist_ok=True)
    file_names = []
    f_cap = (album_dir / 'captions.csv').open('w')
    request = service.mediaItems().search(body={'albumId': album_id})
    while request is not None:
      response = request.execute()
      media_files = response.get('mediaItems', [])
      for media_file in media_files:
        file_name = media_file['filename']
        file_names.append(file_name)
        file_path = album_dir / file_name
        _, file_ext = os.path.splitext(file_path)
        download_url = f"{media_file['baseUrl']}=dv" if file_ext.lower() in VID_EXTS else f"{media_file['baseUrl']}=d"

        if not file_path.is_file():
          dl_count = 0
          while dl_count <= max_retries:
            try:
              print(f'Downloading file {file_name} ({dl_count+1}).', end='')
              download_file(download_url, file_path)
            except Exception as e:
              dl_count += 1
              logging.exception('Connection error.')
            else:
              break
        else:
            print(f'Skip downloading file {file_name}.', end='')

        user_comment = media_file.get('description', '')  # default to an empty string if 'description' not found
        print(f' Description: {user_comment}' if user_comment else ' Without description.')
        creation_time = parser.parse(media_file['mediaMetadata']['creationTime'])
        save_metadata(str(file_path), user_comment, creation_time, file_ext)
    
      f_cap.write(f'{file_name}\t{user_comment}\n')
      request = service.mediaItems().list_next(request, response)

    f_cap.close()

    duplicates = [item for item, count in collections.Counter(file_names).items() if count > 1]
    if duplicates:
        print('Photos with duplicated file names that were not copied: ', ', '.join(duplicates))
  
    local_files = [f.name for f in album_dir.iterdir() if f.is_file() and not f.name.endswith('.csv')]
    not_on_server = np.setdiff1d(local_files, file_names)
    if not_on_server.size > 0:
        print('\nFiles that do not exist on the server:')
        print('\n'.join(not_on_server))


if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('-a', '--albums',
    type=str,
    nargs='+',
    default=['all'],
    help="A list of album names to backup. Backup everything if set to 'all' (default: %(default)s).")
  ap.add_argument('-d', '--dir',
    type=Path,
    default=Path.home() / 'Pictures',
    help="A directory where downloaded album folders will be stored (default: %(default)s).")
  ap.add_argument('-r', '--max_retries',
    type=int,
    default=3,
    help="Maximum number of download retries (default: %(default)d).")
  args = ap.parse_args()
  gphotos_backup(args.dir, args.albums, args.max_retries)
