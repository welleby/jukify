from flask import (Blueprint, jsonify, request, redirect, session)

import tekore as tk

client_id, client_secret, redirect_uri = tk.config_from_environment()

cred = tk.Credentials(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
auth = tk.UserAuth(cred, scope=tk.scope.every)

#spotify = tk.Spotify(token)
#tracks = spotify.playlist_items('6brdBoGEtbthpJ8hyddIiV', market='SE',limit=10, fields='items(track(uri,duration_ms,name,artists(name)))')

bp = Blueprint('spotify_connect', __name__, url_prefix='/spotify')

def store_user_tokens(token):
    session['refresh_token'] = token.refresh_token #Store in db
    session['access_token'] = token.access_token
    return 1

def store_access_token(token):
    session['access_token'] = token.access_token
    return 1

# Start initial authorization flow in spotifys OAuth 
@bp.route('/auth/request_token', methods=('GET', 'POST'))
def request_token():
    return redirect(auth.url, code=302)

# Start refresh token flow in spotifys OAuth 
@bp.route('/auth/refresh_token', methods=('GET', 'POST'))
def refresh_token():
    refresh_token = request.args.get('refresh_token')
    token = tk.refresh_user_token(client_id, client_secret, refresh_token)
    store_access_token(token)
    return get_playlist()

# callback called from spotify OAuth2 flow
@bp.route('/auth/callback', methods=('GET', 'POST'))
def callback():
    content = request.get_json()
    print(jsonify(request.args))
    print(request.args.get('code'))
    print(request.args.get('state'))
    token = auth.request_token(request.args.get('code'), request.args.get('state'))
    store_user_tokens(token)
    return get_playlist()

def get_playlist():
    spotify = tk.Spotify(session['access_token'])
    tracks = spotify.playlist_items('6brdBoGEtbthpJ8hyddIiV', market='SE',limit=10, fields='items(track(uri,duration_ms,name,artists(name)))')
    return jsonify(tracks)


def get_or_update_token(redirect, refresh_token):
    if 'access_token' not in session:
        token = tk.refresh_user_token(client_id, client_secret, refresh_token)
        store_access_token(token)
        return token
    else:
        return session['access_token']

@bp.route('/playlist', methods=('GET', 'POST'))
def playlist():
    token = get_or_update_token("/spotify/playlist",'')
    spotify = tk.Spotify(token)
    tracks = spotify.playlist_items('6brdBoGEtbthpJ8hyddIiV', market='SE',limit=10, fields='items(track(uri,duration_ms,name,artists(name)))')
    return jsonify(tracks)
