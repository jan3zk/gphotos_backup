from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import glob
import argparse
import os
import numpy as np
import webbrowser


def simple_get(url):
  '''
  Attempts to get the content at `url` by making an HTTP GET request.
  If the content-type of response is some kind of HTML/XML, return the
  text content, otherwise return None.
  '''
  try:
    with closing(get(url, stream=True)) as resp:
      if is_good_response(resp):
        return resp.content
      else:
        return None

  except RequestException as e:
    print('Error during requests to {0} : {1}'.format(url, str(e)))
    return None

def is_good_response(resp):
  '''
  Returns True if the response seems to be HTML, False otherwise.
  '''
  content_type = resp.headers['Content-Type'].lower()
  return (resp.status_code == 200
      and content_type is not None 
      and content_type.find('html') > -1)

def main():
  web_albums = [] #web albums
  web_size = [] #web album size
  ext_albums = [] #extra albums
  dl_albums = [] #local albums
  dl_size = [] #local album size
  ndl_albums = [] #albums that are not downloaded yet

  webbrowser.open('https://photos.google.com/albums')
  input('''The opened web site should be saved as a HTML only web page to the 
  folder of this repo. When finished, press <Enter> to continue...''')
  print('\nA list of all web albums:')
  raw_html = open('Albums - Google Photos.html')
  html = BeautifulSoup(raw_html, 'html.parser')
  walbums = html.findAll("div", {"jsname": "apz4bc"})
  wsize = html.findAll("div", {"class": "UV4Xae"})
  for album, ws in zip(walbums, wsize):
    web_albums.append(album.text)
    web_size.append([int(s) for s in ws.text.split() if s.isdigit()][0])
    print(album.text+' ('+ws.text+')')

  print('\nA list of local albums:')
  albums = sorted(glob.glob(args.dir+'/*/'),reverse=True)
  for album in albums:
    dl_album = album.split(os.sep)[-2]
    dl_albums.append(dl_album)
    ds = len(glob.glob(album+'*.jpg'))+len(glob.glob(album+'*.JPG'))+\
      len(glob.glob(album+'*.jpeg'))+len(glob.glob(album+'*.JPEG'))+\
      len(glob.glob(album+'*.png'))+len(glob.glob(album+'*.PNG'))+\
      len(glob.glob(album+'*.avi'))+len(glob.glob(album+'*.AVI'))+\
      len(glob.glob(album+'*.mov'))+len(glob.glob(album+'*.MOV'))+\
      len(glob.glob(album+'*.mp4'))+len(glob.glob(album+'*.MP4'))+\
      len(glob.glob(album+'*.wmv'))+len(glob.glob(album+'*.WMV'))
    dl_size.append(ds)
    print(dl_album+' ('+str(ds)+')')

  print('\nA list of albums that were not downloaded yet:')
  ndl_albums = np.setdiff1d(web_albums, dl_albums)
  ndl_albums = ndl_albums.tolist()
  for ndl_album in ndl_albums:
    print(ndl_album)

  print('\nA list of downladed extra albums (shared albums, deleted web albums, etc.):')
  ext_albums = np.setdiff1d(dl_albums, web_albums)
  ext_albums = ext_albums.tolist()
  for ext_album in ext_albums:
    print(ext_album)

  print('\nA list of albums with different number of photos/videos:')
  for idx, album in enumerate(dl_albums):
    if album in web_albums:
      ws = web_size[web_albums.index(album)] 
      ds = dl_size[idx]
      if ws != ds:
        print(album+' (local: '+str(ds)+', web: '+str(ws)+')')

  print('\nStats:')
  print(' - no. of web albums: '+str(len(web_albums)))
  print(' - no. of downloaded albums: '+str(len(dl_albums)))
  print(' - no. of albums that exist only on the server side: '+str(len(ndl_albums)))
  print(' - no. of albums that exist only on the local side: '+str(len(ext_albums)))


if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument(
    '-d','--dir',
    type = str,
    default = os.path.expanduser('~/Pictures'),
    help = ''' 
    Albums directory.
    '''
  )
  args = ap.parse_args()
  main()
