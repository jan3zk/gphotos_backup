# Google Photos Backup

## Overview

Google Photos Backup downloads Google Photos web albums to the local drive. The photos in each album are downloaded to a separate folder, while the photo comments are embedded in the EXIF metadata.<sup id="a1">[1](#f1)</sup> This app only serves as a local backup and cannot upload photos to Google Photos.

## Installation

The code runs in Python 3. Before running any script, install the dependencies with ```pip install -r requirements.txt```.

### Authorize access

The app needs authorization to read from Google Photos. For this purpose, the credentials file should be created. Go to the [https://developers.google.com/photos/library/guides/get-started](https://developers.google.com/photos/library/guides/get-started) page and click the "Enable the Google Photos Library API" button. Select "Create new project". Enter arbitrary project name and product name. In the "Where are you calling from?" field, select the "Desktop app" and click the "CREATE" button and then "DOWNLOAD CLIENT CONFIGURATION", which will download the credentials.json file. Move the file to the folder of this repository. If needed, all subsequent downloads of the credentials file can be performed from the [https://console.developers.google.com/apis/credentials](https://console.developers.google.com/apis/credentials).

## Usage

### Download album(s)

Run ```python gphotos_backup.py``` to backup all albums, or add the argument ```-a 'album name'``` to create a backup of the specified album.

### View albums locally

To view locally downloaded albums, it is recomended to use [Nomacs](https://nomacs.org), where you can open the album folder by selecting "File > Open Directory" from the menu. Image comments can be viewed by selecting "Panels > Metadata". Right click on the [panel](https://nomacs.org/metadata-hud), select the "Change entries" and make sure that the "Exif > Image > ImageDescription" is selected.  

#### Optional: Show differences between the local and remote

Run ```python quick_check_albums.py``` to display the differences between the local and remote album collections. This command compares only the album names and the number of files in each album between the local and remote collections.

#### Optional: Search comments

To allow a fast photo comment search, all comments in each album are also stored in a *.csv file in a folder associated with that album. A fast search for a specific text in the comments can be performed in terminal with ```grep -Ri --include \*.csv "text to search" path/to/albums```.

## Other backup alternatives

The [rclone](https://rclone.org/googlephotos/) backend for Google Photos is a specialized backend for transferring photos and videos to and from Google Photos. Compared to this app, the main disadvantage of rclone is that it discards photo comments.

<b id="f1">1</b> Note that if you edit your photo on a server side after backup procedure is performed, re-running the backup will not update the edited photo on the local side, since the API does not provide the date when the photo was last edited. To update such photos, you need to delete them manually on the local side and rerun the backup command. [↩](#a1)
