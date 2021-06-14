# GPhotos Backup

## Overview

GPhotos Backup downloads web albums on Google Photos to the local drive. Photos in each album are downloaded into the separate folder, while the photo comments are embedded into EXIF metadata.<sup id="a1">[1](#f1)</sup>

## Installation

Code runs in Python 3. Before you run any python script install dependencies with ```pip install -r requirements.txt```.

## Usage

### Create credentials

In order for the application to work the credentials file should be created. Go to the [https://developers.google.com/photos/library/guides/get-started](https://developers.google.com/photos/library/guides/get-started) and click on the "Enable the Google Photos Library API" button. Select "Create new project". Enter the arbitrary project name and product name. In the "Where are you calling from?" field choose the "Desktop app" and press the button "CREATE" and then "DOWNLOAD CLIENT CONFIGURATION" which downloads the credentials.json file. Move the file into the folder of this repository. If needed, all subsequent downloads of the credentials file can be performed from the [https://console.developers.google.com/apis/credentials](https://console.developers.google.com/apis/credentials).

### Download album(s)

Run ```python gphotos_backup.py``` to backup all albums or add the argument ```-a 'album name'``` to make a backup of the specified album.

### Optional: Show differences between the local and the remote

Run ```python quick_check_albums.py``` to show diff statistics between local and remote album collections. This command only compares album names and file counts in each album between the local and the remote.

### Optional: Search captions

To enable a fast caption search, all photo captions in each album are also saved to the *.csv file in a folder pertaining to the corresponding album. Fast search for specific text in captions can be performed in terminal by ```grep -Ri --include \*.csv "text to search" path/to/albums```.

## Other backup alternatives

[Rclone](https://rclone.org/googlephotos/) backend for Google Photos is a specialized backend for transferring photos and videos to and from Google Photos. Compared to this app, the main disadvantage of rclone is that it discards photo captions.

<b id="f1">1</b> Note that if you edit your photo on a server side after you perform the backup procedure, re-running the backup will not update the edited photo on the local side, since the API doesn't provide the date when the photo was last edited. In order to update such photos you have to manually delete them on the local side and rerun the backup command. [↩](#a1)
