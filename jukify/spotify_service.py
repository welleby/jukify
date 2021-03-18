import tekore as tk
from tekore import (Token, scope)
from flask import jsonify
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

class TokenError(RuntimeError):
    def __init__(self, arg):
        self.args = arg

class MissingToken(TokenError):
    def __init__(self, arg):
        self.args = arg

class ExpiringToken(TokenError):
    def __init__(self, arg):
        self.args = arg

class SpotifyService:
    
    def __init__(self):
        self.config_file = "config/spotify_credentials"
        self.client_id, self.client_secret, self.redirect_uri, self.refresh_token  = tk.config_from_file(self.config_file, return_refresh=True)
        self.cred = tk.Credentials(client_id=self.client_id,client_secret=self.client_secret,redirect_uri=self.redirect_uri)
        self.auth = tk.UserAuth(self.cred, scope=tk.scope.every)
        self.user_token = token_from_string(self.refresh_token)
        pass

    def get_auth_url(self):
        return self.auth.url

    def handle_callback(self, code, state):
        token = self.auth.request_token(code,state)
        self.__store_user_token(token)
        return

    def play_tracks(self,tracks):
        try:
            spotify = self.__get_spotify()
            devices = spotify.playback_start_tracks([tracks], device_id=settings['spotify']['device_id'])
            return
        except MissingToken:
            raise TokenError("Missing Token")

    def play_track_from_playlist(self,index):
        try:
            tracks = self.get_playlist()
            spotify = self.__get_spotify()
            track = tracks['items'][int(index)%len(tracks['items'])]['track']
            devices = spotify.playback_start_tracks([track['id']], device_id=settings['spotify']['device_id'])
            return
        except MissingToken:
            raise TokenError("Missing Token")

    def get_playlist(self):
        try:
            spotify = self.__get_spotify()
            tracks = spotify.playlist_items(settings['spotify']['playlist'], market='SE',limit=10, fields='items(track(id,duration_ms,name,artists(name)))')
            return tracks
        except MissingToken:
            raise TokenError("Missing Token")

    def get_devices(self):
        try:
            spotify = self.__get_spotify()
            devices = spotify.playback_devices()
            return devices
        except MissingToken:
            raise TokenError("Missing Token")

    def __store_user_token(self, token):
        tk.config_to_file(self.config_file, (self.client_id, self.client_secret, self.redirect_uri, token.refresh_token))
        self.refresh_token = token.refresh_token
        self.user_token = token
        return

    def __get_spotify(self):
        try:
            token = self.__get_token()
            spotify = tk.Spotify(token)
            return spotify
        except MissingToken:
            raise MissingToken("Missing refresh_token. To solve: Request new token with /auth/request_token")

    def __get_token(self):
        try:
            if self.refresh_token is None:
                raise MissingToken("Missing refresh_token")
            if self.user_token.is_expiring:
                token = tk.refresh_user_token(self.client_id, self.client_secret, self.refresh_token)
                self.__store_user_token(token)
                return token
            else:
                return self.user_token
        except NameError:
            raise MissingToken("user_token undefined")  
