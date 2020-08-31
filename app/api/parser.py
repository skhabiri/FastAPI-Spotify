"""
This  module takes a keyword 'phrase'  and parses
all the albums' tracks and audio features of all the artists
that were related to the keyword. The result is saved as 'dataframe',
as well as being dumped into a csv file
"""
# regardless of being run as a module or script,
# __package__ variable is set properly
if __name__ == '__main__' and  __package__ is None:
    print("__name__ is: {}".format(__name__))
    print("__package__ is: {}".format(__package__))
    print("__file__ is: {}".format(__file__))
    __package__ = "app.api"
else:
    print("__name__ is: {}".format(__name__))
    print("__package__ is: {}".format(__package__))
    print("__file__ is: {}".format(__file__))


from pprint import pprint
import time
import numpy as np
import pandas as pd
# from typing import List

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .settings import *
from fastapi import APIRouter


# all the keys are read from .env located in the parent directory
client_cred = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_cred)

router = APIRouter()


def spotify_parser(phrase: str):
    """
    An API call to Spotify, to search for a
    keyword and return a list of dictionaries
    containing the artist, album and track names
    ex/ key_word = {"california dreamin"}
    :return:
    """

    # # a random api call to spotify based on a trackID in database
    # songs = db.query(Songdb).order_by(func.random()).all()

    # Search Spotify for a keyword:
    result = sp.search(phrase, limit=5)

    record_list = []
    for item in range(len(result['tracks']['items'])):
        """
        The memory location of of keyword_dict needs to change to avoid list mutation 
        hence the keyword_dict construct is inside the loop and not outside.
        """
        keyword_dict = {}
        keyword_dict['artist'] = result['tracks']['items'][item]['artists'][0]['name']
        keyword_dict['album'] = result['tracks']['items'][item]['album']['name']
        keyword_dict['track'] = result['tracks']['items'][item]['name']
        record_list.append(keyword_dict)

    return record_list


def create_csv(phrase: str, filename: str):
    """
    It takes a keyword 'phrase' and parses
    all the albums' tracks and audio features of all the artists
    that were related to the keyword. The result is
    dumped into csv <filename>.
    ex/ spotify_parser({"california dreamin", "Garfunkel"})
    """

    # Search Spotify for a keyword:
    result = sp.search(phrase, limit=1)
    print("keyword result is:\n", result)

    # Extract artist uri of the first Artist in each of the 'items':
    artists_uris = []
    for item in range(len(result['tracks']['items'])):
        artists_uris.append(result['tracks']['items'][item]['artists'][0]['uri'])
    # print("artists uris:",  artists_uris)

    # Pull all of the albums for all the artists extracted above:
    all_albums_raw = []
    all_albums_raw = [sp.artist_albums(aruri, album_type='album') for aruri in artists_uris]
    print("all_albums json format :\n", all_albums_raw)

    # Store album names, album uris, and artist names in separate lists:
    all_album_names = []
    all_album_uris = []
    all_artist_names = []
    for dic_albums in all_albums_raw:
        for albumuri in range(len(dic_albums['items'])):
            all_album_names.append(dic_albums['items'][albumuri]['name'])
            all_album_uris.append(dic_albums['items'][albumuri]['uri'])
            all_artist_names.append(dic_albums['items'][albumuri]['artists'][0]['name'])

    print("all album names are:\n", all_album_names)
    print("all album uris are:\n", all_album_uris)
    print("all artist names:\n", all_artist_names)

    # Keep names and uris in same order to keep track of duplicate albums
    # We have same album names with different uri and therefore same tracks but different set of uris again

    def album_tracks(aluri):
        """
        create a dictionary of all the songs in an album
        """
        albums[aluri] = {}
        # Create keys-values of empty lists inside nested dictionary for album
        # aluri is already the key for album nested dictionary.
        # However, since later, when in converting the nested dictionary
        # to flat dictionary and then dataframe, the keys are dropped,
        # we also add the same aluri as a sub key (column feature for dataframe),
        # to have it available in final dataframe
        albums[aluri]['album'] = []
        albums[aluri]['aluri'] = []
        albums[aluri]['track_number'] = []
        albums[aluri]['trid'] = []
        albums[aluri]['name'] = []
        albums[aluri]['artist'] = []
        albums[aluri]['arid'] = []

        # pull data on album tracks
        tracks = sp.album_tracks(aluri)
        for n in range(len(tracks['items'])):
            albums[aluri]['album'].append(all_album_names[album_count])
            albums[aluri]['aluri'].append(aluri)
            albums[aluri]['track_number'].append(tracks['items'][n]['track_number'])
            albums[aluri]['trid'].append(tracks['items'][n]['id'])
            albums[aluri]['name'].append(tracks['items'][n]['name'])
            albums[aluri]['artist'].append(tracks['items'][n]['artists'][0]['name'])
            albums[aluri]['arid'].append(tracks['items'][n]['artists'][0]['id'])

    # parse tracks of all albums
    albums = {}
    album_count = 0
    for aluri in all_album_uris:  # each album
        album_tracks(aluri)
        print(str(all_album_names[album_count]) + " album tracks has been added to all_albums dictionary")
        album_count += 1  # Updates album count once all tracks have been added

    # adding audio features for each track to the existing albums dictionary
    def audio_features(aluri):
        # Add new key-values to store audio features
        albums[aluri]['acousticness'] = []
        albums[aluri]['danceability'] = []
        albums[aluri]['energy'] = []
        albums[aluri]['instrumentalness'] = []
        albums[aluri]['liveness'] = []
        albums[aluri]['loudness'] = []
        albums[aluri]['speechiness'] = []
        albums[aluri]['tempo'] = []
        albums[aluri]['valence'] = []
        albums[aluri]['popularity'] = []

        track_count = 0
        for track in albums[aluri]['trid']:
            # pull audio features per track
            features = sp.audio_features(track)

            # Append to relevant key-value
            albums[aluri]['acousticness'].append(features[0]['acousticness'])
            albums[aluri]['danceability'].append(features[0]['danceability'])
            albums[aluri]['energy'].append(features[0]['energy'])
            albums[aluri]['instrumentalness'].append(features[0]['instrumentalness'])
            albums[aluri]['liveness'].append(features[0]['liveness'])
            albums[aluri]['loudness'].append(features[0]['loudness'])
            albums[aluri]['speechiness'].append(features[0]['speechiness'])
            albums[aluri]['tempo'].append(features[0]['tempo'])
            albums[aluri]['valence'].append(features[0]['valence'])
            # popularity is stored elsewhere
            track_pop = sp.track(track)
            albums[aluri]['popularity'].append(track_pop['popularity'])
            track_count += 1

    sleep_min = 2
    sleep_max = 5
    start_time = time.time()

    # pause randomly after every 5 albums
    request_count = 0
    for albumuri in albums:
        audio_features(albumuri)
        request_count += 1
        if request_count % 5 == 0:
            print(str(request_count) + " albums completed")
            time.sleep(np.random.uniform(sleep_min, sleep_max))
            # print('Album #: {} added'.format(request_count))
            print('Elapsed Time: {} seconds'.format(time.time() - start_time))

    # In spotify_albums for each album_uri there is a key
    # and inside each album_uri key there are bunch of features

    # In dic_df we remove the album_uri keys and flatten the
    # nested dictionary in a tidy (long) format, suitable for dataframe
    # In other word there is one row for each track of any album. This also
    # alows to remove the duplicate rows based on a certain column,
    # despite having different track_uris

    # Initialize the dataframe
    dic_df = {}
    for feature in list(albums.values())[0]:
        dic_df[feature] = []
    print("empty dic_df: ", dic_df['loudness'])

    for aluri in albums:
        for feature in albums[aluri]:
            dic_df[feature].extend(albums[aluri][feature])

    print("Total number of rows in flatten dictionary:\n", len(dic_df['album']))

    dataframe = pd.DataFrame.from_dict(dic_df)
    pprint(dataframe)
    print(f"writing to {filename} file ......")
    with open(filename, 'w+') as f:
        dataframe.to_csv(f, mode='w+')
    # albums is a nested dictionary. dic_df is a flat long dictionary format

    return albums


if __name__ == '__main__':
    albums = create_csv('wonderful world', 'spotify_music.csv')
