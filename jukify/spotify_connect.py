from flask import (Blueprint, jsonify, request, redirect, session)

import tekore as tk
from tekore import (Token, scope)
from . settings import settings

def token_from_string(refresh_token_str):
    token_info = {
        "access_token": '',
        "token_type": 'Bearer',
        "scope": str(tk.scope.every),
        "refresh_token": refresh_token_str,
        "expires_in": 0
    }
    return Token(token_info=token_info, uses_pkce=False)

config_file = "config/spotify_credentials"

# client_id, client_secret, redirect_uri = tk.config_from_environment()
client_id, client_secret, redirect_uri, refresh_token  = tk.config_from_file(config_file, return_refresh=True)
#conf  = tk.config_from_file(config_file)

cred = tk.Credentials(client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)
auth = tk.UserAuth(cred, scope=tk.scope.every)
global user_token
user_token = token_from_string(refresh_token)

bp = Blueprint('spotify_connect', __name__, url_prefix='/spotify')


class TokenError(RuntimeError):
   def __init__(self, arg):
      self.args = arg

class MissingToken(TokenError):
   def __init__(self, arg):
      self.args = arg

class ExpiringToken(TokenError):
   def __init__(self, arg):
      self.args = arg

# Start initial authorization flow in spotifys OAuth 
@bp.route('/auth/request_token', methods=('GET', 'POST'))
def request_token():
    return redirect(auth.url, code=302)

# callback called from spotify OAuth2 flow
@bp.route('/auth/callback', methods=('GET', 'POST'))
def callback():
    token = auth.request_token(request.args.get('code'), request.args.get('state'))
    store_user_token(token)
    return "Done"

# callback called from spotify OAuth2 flow
@bp.route('/play', methods=('GET', 'POST'))
def play():
    spotify = get_spotify()
    devices = spotify.playback_start_tracks([request.args.get('track_id')], device_id=settings['spotify']['device_id'])
    return jsonify(spotify.playback_devices())

@bp.route('/playlist', methods=('GET', 'POST'))
def playlist():
    try:
        spotify = get_spotify()
        tracks = spotify.playlist_items(settings['spotify']['playlist'], market='SE',limit=10, fields='items(track(uri,duration_ms,name,artists(name)))')
        return jsonify(tracks)
    except MissingToken:
        return redirect(auth.url, code=302)

def store_user_token(token):
    tk.config_to_file(config_file, (client_id, client_secret, redirect_uri, token.refresh_token))
    global refresh_token
    refresh_token = token.refresh_token
    global user_token 
    user_token = token
    return

def get_spotify():
    try:
        token = get_token()
        spotify = tk.Spotify(token)
        return spotify
    except MissingToken:
        raise MissingToken("Missing refresh_token. To solve: Request new token with /auth/request_token")

def get_token():
    try:
        global user_token
        if refresh_token is None:
            raise MissingToken("Missing refresh_token")
        if user_token.is_expiring:
            token = tk.refresh_user_token(client_id, client_secret, refresh_token)
            store_user_token(token)
            return token
        else:
            return user_token
    except NameError:
        raise MissingToken("user_token undefined")  
