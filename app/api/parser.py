"""
This  module takes a keyword 'phrase'  and parses
all the albums' tracks and audio features of all the artists
that were related to the keyword. The result is saved as 'dataframe',
as well as being dumped into a csv file
"""

# regardless of being run as a module or script,
# __package__ variable is set properly
if __name__ == '__main__' and  __package__ is None:
    print("runs as a python script not module")
    print("__name__ is: {}".format(__name__))
    print("__package__ is: {}".format(__package__))
    print("__file__ is: {}".format(__file__))
    __package__ = "app.api"

else:
    print("runs as a module not python script")
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


# all the keys are read from .env located in the project directory
client_cred = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_cred)

router = APIRouter()

def spotify_parser(phrase: str, limit: int):
    """
    An API call to Spotify, to search for a
    keyword and return a list of dictionaries with three keys for each of "limit" number of items
    :return:
    record_list = [{"artist":<value>, "album":<value>,"track":<value>}, {...}, ...]

    > spotify_parser({"california dreamin", "Garfunkel"})
    [{'artist': 'The Mamas & The Papas', 'album': 'If You Can Believe Your Eyes & Ears', 
    'track': "California Dreamin' - Single Version"}, {'artist': 'Bobby Womack', 
    'album': 'Fly Me To The Moon', 'track': "California Dreamin'"}, 
    {'artist': 'The Mamas & The Papas', 'album': 'If You Can Believe Your Eyes And Ears', 
    'track': "California Dreamin'"}, {'artist': 'Hollywood Undead', 'album': 'Five', 
    'track': 'California Dreaming'}, {'artist': 'Sia', 
    'album': 'San Andreas (Original Motion Picture Soundtrack)', 
    'track': "California Dreamin'"}]
    """

    # # a random api call to spotify based on a trackID in database
    # songs = db.query(Songdb).order_by(func.random()).all()

    # Search Spotify for a keyword:
    result = sp.search(phrase, limit)
    """
    > result.keys()
    dict_keys(['tracks'])
    
    > result['tracks'].keys()
    dict_keys(['href', 'items', 'limit', 'next', 'offset', 'previous', 'total'])
    
    > len(result['tracks']['items'])
    5
    
    > result['tracks']['items'][0].keys()
    dict_keys(['album', 'artists', 'available_markets', 'disc_number', 
    'duration_ms', 'explicit', 'external_ids', 'external_urls', 'href', 
    'id', 'is_local', 'name', 'popularity', 'preview_url', 'track_number', 'type', 'uri'])

    > result['tracks']['items'][0]['artists'][0].keys()
    dict_keys(['external_urls', 'href', 'id', 'name', 'type', 'uri'])

    > result['tracks']['items'][0]['album'].keys()
    dict_keys(['album_type', 'artists', 'available_markets', 'external_urls', 
    'href', 'id', 'images', 'name', 'release_date', 'release_date_precision', 
    'total_tracks', 'type', 'uri'])

    > result['tracks']['items'][0]['name']
    "California Dreamin' - Single Version"    
    """

    record_list = []
    for item in range(len(result['tracks']['items'])):
        """
        The memory location of keyword_dict needs to change to avoid list mutation 
        hence the keyword_dict construct is inside the loop and not outside.
        """
        keyword_dict = {}
        keyword_dict['artist'] = result['tracks']['items'][item]['artists'][0]['name']
        keyword_dict['album'] = result['tracks']['items'][item]['album']['name']
        keyword_dict['track'] = result['tracks']['items'][item]['name']
        record_list.append(keyword_dict)

    return record_list


def csv_gen(phrase: str, filename: str, limit: int):
    """
    It takes a keyword 'phrase' and parses
    all the tracks and audio features of all the albums of "limit" number of artists
    that were related to the keyword. The result is dumped into a csv <filename>.
    ex/ 
    """

    # Search Spotify for a keyword: limit could be more than 1
    result = sp.search(phrase, limit)
    print("result['tracks']['items'][0].keys():\n", result['tracks']['items'][0].keys())
    
    """
    > result['tracks']['items'][0].keys()
    dict_keys(['album', 'artists', 'available_markets', 'disc_number', 'duration_ms', 
    'explicit', 'external_ids', 'external_urls', 'href', 'id', 'is_local', 'name', 
    'popularity', 'preview_url', 'track_number', 'type', 'uri'])
    """
    
    # Extract artist uri of the first Artist in each of the result['tracks']['items'] list
    artists_uris = []
    for item in range(len(result['tracks']['items'])):
        artists_uris.append(result['tracks']['items'][item]['artists'][0]['uri'])
    """
    > artists_uris
    ['spotify:artist:1bs7HoMkSyQwcobCpE9KpN', 
    'spotify:artist:0vqkz1b2qBkoYrGMj2CUWq']
    """

    # Pull all of the albums for all the artists extracted above:
    all_albums_raw = []
    all_albums_raw = [sp.artist_albums(aruri, album_type='album') for aruri in artists_uris]
    """
    > len(all_albums_raw)
    2

    > all_albums_raw[0].keys()
    dict_keys(['href', 'items', 'limit', 'next', 'offset', 'previous', 'total'])

    > len(all_albums_raw[0]['items'])
    6

    > all_albums_raw[0]['items'][0].keys()
    dict_keys(['album_group', 'album_type', 'artists', 'available_markets', 
    'external_urls', 'href', 'id', 'images', 'name', 'release_date', 
    'release_date_precision', 'total_tracks', 'type', 'uri'])
    """

    """ Store album names, album uris, and artist names of all albums belonging to
    all the artists that match the keyword, in separate lists
    """
    all_album_names = []
    all_album_uris = []
    all_artist_names = []
    
    # one dic_albums per artist
    for dic_albums in all_albums_raw:

        # multiple albums in each dic_albums of each artist
        for artistalbum_idx in range(len(dic_albums['items'])):
            all_album_names.append(dic_albums['items'][artistalbum_idx]['name'])
            all_album_uris.append(dic_albums['items'][artistalbum_idx]['uri'])
            all_artist_names.append(dic_albums['items'][artistalbum_idx]['artists'][0]['name'])

    print("all album names are:\n", all_album_names)
    print("all album uris are:\n", all_album_uris)
    print("all artist names:\n", all_artist_names)

    """
    > all_artist_names
    ['The Mamas & The Papas', 'The Mamas & The Papas', 'The Mamas & The Papas', 
    'The Mamas & The Papas', 'The Mamas & The Papas', 'The Mamas & The Papas', 
    'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 
    'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 
    'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 
    'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 'Bobby Womack', 'Bobby Womack']

    > all_album_names
    ['People Like Us', 'The Papas & The Mamas', 'Deliver', 'The Mamas & The Papas', 
    'If You Can Believe Your Eyes & Ears', 'If You Can Believe Your Eyes And Ears', 
    'The Bravest Man in the Universe', 'The Bravest Man in the Universe', 'The Womack Live', 
    'Traditions', 'Soul Sensation (Live)', 'I Still Love You', '(I Wanna) Make Love To You', 
    Save the Children', 'Save the Children', 'Save the Children', 'Last Soul Man', 'Womagic', 
    'So Many Rivers', "Someday We'll All Be Free", "Someday We'll All Be Free", 'The Poet II', 
    'The Poet', 'Roads of Life', 'Pieces (Expanded Edition)', 'Home Is Where the Heart Is']

    > len(all_album_uris)
    26
    """

    # Keep names and uris in same order to keep track of duplicate albums
    # We have same album names with different uri and therefore same tracks but different set of uris again

    def album_tracks(aluri, album_count, albums, all_album_names):
        """
        create a dictionary of all the songs in an album
        """
        # albums is a global variable defined outside the function
        albums[aluri] = {}
        # Create keys-values of empty lists inside nested dictionary for album
        # aluri is already the key for album nested dictionary.
        # However, since later, when in converting the nested dictionary
        # to flat dictionary and then dataframe, the keys are dropped,
        # we also add the same aluri as a sub key (column feature for dataframe),
        # to have it available in final dataframe
        albums[aluri]['album'] = [] #album name
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
    albums = {}     # define as global variable
    # album_count = 0
    for album_count, aluri in enumerate(all_album_uris):  # each album
        album_tracks(aluri, album_count, albums, all_album_names)
        print(str(all_album_names[album_count]) + ": all tracks added to albums")
        # album_count += 1  # Updates album count once all tracks have been added
    """
    All tracks are in a list under 'trid' key
    > len(albums['spotify:album:4HjNY35duY5p5ntqoyIlpp']['trid'])
    12
    """

    # adding audio features for each track to the existing albums dictionary
    def audio_features(aluri, albums):
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

        # track_count = 0
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
            # track_count += 1
        
        """
        > albums['spotify:album:4HjNY35duY5p5ntqoyIlpp']['valence']
        [0.765, 0.973, 0.716, 0.76, 0.929, 0.855, 0.826, 0.905, 0.787, 0.804, 0.949, 0.879]
        """

    sleep_min = 2
    sleep_max = 5
    start_time = time.time()

    # pause randomly after every 5 albums
    request_count = 0
    # alnumuri is albums key
    for albumuri in albums:
        audio_features(albumuri, albums)
        request_count += 1
        if request_count % 5 == 0:
            print(str(request_count) + " albums completed")
            time.sleep(np.random.uniform(sleep_min, sleep_max))
            # print('Album #: {} added'.format(request_count))
            print('Elapsed Time: {} seconds'.format(time.time() - start_time))

    # In spotify_albums for each album_uri there is a key
    # and inside each album_uri key there are bunch of keys

    # In dic_df we remove the album_uri keys and extend the list of values 
    # for each sub key while removing the albumuri key


    # Initialize the dataframe
    dic_df = {}
    # albums.values() drops the aluri key
    # list(albums.values())[0] is a dictionary for the first aluri
    # feature are the sub keys
    for feature in list(albums.values())[0]:
        dic_df[feature] = []
    print("empty dic_df: ", dic_df['loudness'])

    """
    feature = 'album', 'aluri', 'track_number', 'trid', 'name', 'artist', 
    'arid', 'acousticness', 'danceability', 'energy', 'instrumentalness', 
    'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'popularity'
    """

    # primary key 'aluri' of dictionary 'albums'
    for aluri in albums:
        for feature in albums[aluri]:
            # extend(): Iterates over its argument and adding 
            # each element to the list and extending the list. 
            # dic_df[feature] is a list
            dic_df[feature].extend(albums[aluri][feature])

    """
    > dic_df.keys()
    dict_keys(['album', 'aluri', 'track_number', 'trid', 'name', 'artist', 
    'arid', 'acousticness', 'danceability', 'energy', 'instrumentalness', 
    'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'popularity'])

    > len(dic_df['trid'])
    279
    """
    # keys become columns and list of values rows
    dataframe = pd.DataFrame.from_dict(dic_df)
    pprint(dataframe)
    print(f"writing to {filename} file ......")
    with open(filename, 'w+') as f:
        dataframe.to_csv(f, mode='w+')
    # albums is a nested dictionary. dic_df is a flat long dictionary format

    return len(dataframe), len(albums)


if __name__ == '__main__':
    albums = csv_gen('wonderful world', 'spotify_music.csv')
