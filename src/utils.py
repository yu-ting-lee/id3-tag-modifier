import configparser
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials
from typing import List

config = configparser.ConfigParser()
config.read('config.ini')

CREDENTIALS = SpotifyClientCredentials(
    client_secret=config['SPOTIPY']['CLIENT_SECRET'],
    client_id=config['SPOTIPY']['CLIENT_ID'])

CHARS = ['/', '*', '?', '>', '<', '|', '\\', '"', ':']


def search(query: str) -> List:
    """search tags with the query string"""
    spotify = spotipy.Spotify(client_credentials_manager=CREDENTIALS)
    res = spotify.search(q=query, limit=5)
    return res['tracks']['items']


def escape(file: str) -> str:
    """remove special characters in the filename"""
    for c in CHARS:
        file = file.replace(c, ' ')
    return file
