from flask import (Blueprint, jsonify, request, redirect, session)

import tekore as tk
from . spotify_service import SpotifyService, TokenError

bp = Blueprint('spotify_REST', __name__, url_prefix='/spotify')
service = SpotifyService()


# Start initial authorization flow in spotifys OAuth 
@bp.route('/auth/request_token', methods=('GET', 'POST'))
def request_token():
    return redirect(service.get_auth_url(), 302)

# callback called from spotify OAuth2 flow
@bp.route('/auth/callback', methods=('GET', 'POST'))
def handle_callback():
    service.handle_callback(request.args.get('code'),request.args.get('state'))
    return '',204

# callback called from spotify OAuth2 flow
@bp.route('/play', methods=('GET', 'POST'))
def play_tracks():
    try:
        if 'track_id' not in request.args:
            return "No tracks supplied", 400
        return service.play_tracks(request.args.get('track_id'))
    except TokenError:
        return redirect(auth.url, code=302)
    except tk.NotFound as err:
        return jsonify(err.args), 404

@bp.route('/playlist', methods=('GET', 'POST'))
def get_playlist():
    try:
        return service.get_playlist()
    except TokenError:
        return redirect(auth.url, code=302)

@bp.route('/devices', methods=(['GET']))
def get_devices():
    try:
        return service.get_devices()
    except TokenError:
        return redirect(auth.url, code=302)
