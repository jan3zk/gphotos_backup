# Google Photos Backup

## Overview

Google Photos Backup is a tool designed to download albums from Google Photos to your local drive. Each album gets downloaded to a separate folder. The main advantage of this backup tool over comparable solutions is its ability to preserve photo comments. These comments are not just stored but are directly embedded into the EXIF metadata. This feature facilitates the display of comments alongside the photos in virtually any widely-used image viewer.

Note that this application exclusively functions as a local backup tool, lacking the capability to upload photos to Google Photos. Furthermore, any modifications made to a photo on Google Photos post-backup will not be reflected in the local copy if the backup is run again. This limitation arises because the Google Photos API does not offer details regarding the last edit made to a photo. To ensure your locally stored photos mirror the updated versions on Google Photos, you must manually delete the outdated images from your local storage and execute the backup command once more.

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
