import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from utility import *
from cli import CLI

cli = CLI(sys.argv[1:])

load_env(cli.env_path)

PLAYLIST_NAME = get_env("PLAYLIST_NAME")
ARTIST_ID = get_env("ARTIST_ID")

CLIENT_ID = get_env("CLIENT_ID")
CLIENT_SECRET = get_env("CLIENT_SECRET")

USERNAME = get_env("USERNAME")

SCOPES = ["playlist-modify-private", "playlist-read-private"]

auth_manager = SpotifyOAuth(
    CLIENT_ID, CLIENT_SECRET, username=USERNAME, redirect_uri="http://localhost:8080", scope=" ".join(SCOPES))
sp = spotipy.Spotify(auth_manager=auth_manager)
me = sp.me()

playlist: dict | None = None
playlists = sp.user_playlists(me["id"])["items"]

for p in playlists:
    if p["name"] == PLAYLIST_NAME:
        permitted = True
        if cli.interactive:
            prompt = f"Do you want to overwrite the playlist {PLAYLIST_NAME}?"
            permitted = decide(prompt, ["y", "n"]) == "y"

        if permitted:
            playlist = sp.playlist(p["id"])
            break

if playlist is None:
    artist_name = sp.artist(ARTIST_ID)["name"]
    playlist = sp.user_playlist_create(me["id"], PLAYLIST_NAME,
                                       public=False, collaborative=False, description=f"All songs made by {artist_name} (auto generated)")

tracks = Collection()
tracks.all = get_all_tracks(sp, playlist)
tracks.flush_callback = lambda: sp.playlist_add_items(
    playlist["id"], [x["uri"] for x in tracks.current]) if tracks.current else None


r = Ruleset(
    excluded_tracks=get_env("EXCLUDED_TRACKS").split(","),
    excluded_track_substr=get_env("EXCLUDED_TRACK_SUBSTR").split(","),
    excluded_albums=get_env("EXCLUDED_ALBUMS").split(",")
)

albums = sp.artist_albums(ARTIST_ID)["items"]
failed_request_counter = 0
for album_raw in albums:
    album = sp.album(album_raw["id"])
    if not r.is_album_valid(album):
        continue
    for track in r.validated_tracks(ARTIST_ID, album["tracks"]["items"], tracks):
        tracks.append(track)
    try:
        tracks.flush()
    except spotipy.exceptions.SpotifyException as e:
        failed_request_counter += 1
        print(f"Failed requests: {failed_request_counter}")
        continue
