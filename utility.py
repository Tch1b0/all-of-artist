import os
import math
from typing import TypeVar, Callable
from dotenv import load_dotenv
from spotipy import Spotify


def load_env(path: str | None = None) -> None:
    load_dotenv(dotenv_path=path)


def get_env(key: str):
    return os.environ[key]


def decide(prompt: str, options: list[str]):
    val = None
    while val not in options:
        val = input(f"{prompt} ({'/'.join(options)}) ")
    return val


T = TypeVar("T")


class Collection:
    all: list[T]
    current: list[T]

    flush_callback: Callable

    def __init__(self) -> None:
        self.all = []
        self.current = []

    def append(self, *values: list[T]):
        self.all.extend(values)
        self.current.extend(values)

    def on_flush(self, callback: Callable):
        self.flush_callback = callback

    def flush(self):
        self.flush_callback()
        self.current = []


class Ruleset:
    excluded_tracks: list[str]
    excluded_track_substr: list[str]
    excluded_albums: list[str]

    def __init__(self, excluded_tracks: list[str], excluded_track_substr: list[str], excluded_albums: list[str]) -> None:
        self.excluded_tracks = [x for x in excluded_tracks if x != ""]
        self.excluded_track_substr = [
            x for x in excluded_track_substr if x != ""]
        self.excluded_albums = [x for x in excluded_albums if x != ""]

    def __is_artist_in_track(self, artist_id: str, track: dict) -> bool:
        return any(a["id"] == artist_id for a in track["artists"])

    def validated_tracks(self, artist_id: str, tracks: list[dict], col: Collection):
        new_tracks = []
        for track in tracks:
            name = track["name"]
            is_in_track = self.__is_artist_in_track(artist_id, track)
            contains_excluded_substr = any(
                x in name for x in self.excluded_track_substr) if len(self.excluded_tracks) > 0 else False
            if (is_in_track and 
                name not in self.excluded_tracks and 
                not contains_excluded_substr and 
                not any(t["name"].lower() == name.lower() for t in col.all)):
                new_tracks.append(track)
        return new_tracks

    def is_album_valid(self, album: dict) -> bool:
        return album["name"] not in self.excluded_albums


def get_all_tracks(sp: Spotify, playlist: dict) -> list[dict]:
    tracks = []
    size = playlist["tracks"]["total"]
    for i in range(1, math.ceil(size/50)):
        raw_response = sp.playlist_tracks(
            playlist["id"], offset=((i - 1) * 50), limit=(i * 50))
        tracks.extend([x["track"] for x in raw_response["items"]])
    return tracks
