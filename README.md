# Google Photos Backup

## Overview

Google Photos Backup is a tool designed to download albums from Google Photos to your local drive. Each album gets downloaded to a separate folder, with photo comments embedded directly into the EXIF metadata.<sup id="a1">[1](#f1)</sup> Please note, this application solely serves as a local backup tool and does not provide functionality to upload photos to Google Photos.

## Installation

This application requires Python 3 to run. Before executing any scripts, ensure you've installed the necessary dependencies with ```pip install -r requirements.txt```.

### Granting Access

Google Photos Backup requires authorization to access Google Photos. To facilitate this, you will need to generate a credentials file. Follow the steps below:

1. Visit the [Google Photos Library API page](https://developers.google.com/photos/library/guides/get-started).
2. Click on "Enable the Google Photos Library API".
3. Select "Create new project".
4. Enter your chosen project name and product name.
5. In the "Where are you calling from?" field, select "Desktop app".
6. Click the "CREATE" button, then "DOWNLOAD CLIENT CONFIGURATION". This action downloads the `credentials.json` file.
7. Move the `credentials.json` file into this repository's folder.

If you need to download the credentials file again in the future, you can do so from the [Google API Console](https://console.developers.google.com/apis/credentials).

## Usage

### Downloading Album(s)

Execute ```python gphotos_backup.py``` to backup all albums. Alternatively, you can specify a particular album by adding the argument ```-a 'album name'``` for a targeted backup.

### Viewing Albums Locally

We recommend [Nomacs](https://nomacs.org) for viewing your downloaded albums. Open the album folder via "File > Open Directory". You can access the image comments by navigating to "Panels > Metadata". In the [metadata panel](https://nomacs.org/metadata-hud), right-click, select "Change entries", and ensure that "Exif > Image > ImageDescription" is selected.

#### Optional: Compare Local and Remote Albums

Run ```python quick_check_albums.py``` to identify differences between your local and remote album collections. This script only compares the album names and the number of files in each album.

#### Optional: Search Comments

For efficient searching within photo comments, each album's comments are stored in a *.csv file in the associated album folder. To search for specific text in the comments, use the following terminal command: ```grep -Ri --include \*.csv "text to search" path/to/albums```.

## Alternative Backup Options

The [rclone](https://rclone.org/googlephotos/) backend for Google Photos is an option for transferring photos and videos to and from Google Photos. However, one main downside of rclone when compared to our tool is its lack of support for preserving photo comments.

<b id="f1">1</b> Please be aware that if you edit your photo on Google Photos after the backup process, re-running the backup will not update the edited photo locally. This is due to the Google Photos API not providing information on when the photo was last edited. To update such photos, you need to manually delete them on the local side and rerun the backup command. [↩](#a1)
