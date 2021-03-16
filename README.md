# jukify
Spotify Jukebox project for raspberry pi and old jukebox


#! /bin/bash
export SPOTIFY_CLIENT_ID='client_id'
export SPOTIFY_CLIENT_SECRET='client_secret'
export SPOTIFY_REDIRECT_URI='callback_uri'
export FLASK_APP=jukify
export FLASK_ENVIRONMENT=development
source ./venv/bin/activate
