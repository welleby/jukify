# jukify
Spotify Jukebox project for raspberry pi and old jukebox


source this:
```bash
#! /bin/bash
export SPOTIFY_CLIENT_ID='client_id'
export SPOTIFY_CLIENT_SECRET='client_secret'
export SPOTIFY_REDIRECT_URI='callback_uri'
export FLASK_APP=jukify
export FLASK_ENV=development
source ./venv/bin/activate
```

Spotify users refresh_token will be stored (together with client_id/secret) in ./config/spotifycredentials

## Overview
This Application uses python with flask for a basic REST-interface.

The user needs to authorize spotify app using http://127.0.0.1/spotify/auth/request_token for first time use. This will trigger spotifys OAuth2 flow and store a user-token which will be used for all future requests.

Once done, app will listen for Jukebox-button-presses (connected to rpi GPIO) and play corresponding song from a predefined playlist.

App will also update a seven-segment-display on jukebox (also connected to rpi GPIO).

## Prerequisites
* Jukebox-buttons connected to rpi GPIO
* Jukebox-seven-segment-display connected to rpi GPIO
* Raspberry Pi audio connected to speakers of jukebox
* [raspotify](https://github.com/dtcooper/raspotify) installed and running on rpi (to play audio on this spotify-device)
* Registered Spotify App

## Setup
./jukify/settings.py contains static setup for things like playlist-id (to choose songs from), and device-id (to play audio on)

The ambition is to implement auto-discovery in this app and create an android configuration-app.