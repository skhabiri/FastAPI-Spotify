"""
Radar plot of audio features for a trackId
"""
""" 
When run as a module or when __package__ is not None:
from .filename import *    or
form api.filename import *

when the .py file is a script (__package__ is None and __name__ == __main__):
from filename import *
"""

if __name__ == '__main__' and  __package__ is None:
    print("__name__ is: {}".format(__name__))
    print("__package__ is: {}".format(__package__))
    print("__file__ is: {}".format(__file__))
    __package__ = "app.api"
else:
    print("__name__ is: {}".format(__name__))
    print("__package__ is: {}".format(__package__))
    print("__file__ is: {}".format(__file__))

from fastapi import APIRouter, HTTPException
import pandas as pd
import plotly.express as px
import joblib
# from .predict import FILENAME, csv_url

FILENAME = "./app/api/BW_Spotify_Final.joblib"
csv_url = "./app/api/BW_Spotify_Final.csv"
router = APIRouter()


# Import the prediction model
knn = joblib.load(FILENAME)
new_df = pd.read_csv(csv_url)


# Comes from the colab file containing the prediction model
def predict_model(track_id):

    obs = new_df.index[new_df['id'] == track_id]
    series = new_df.iloc[obs, 5:].to_numpy()

    neighbors = knn.kneighbors(series)
    new_obs = neighbors[1][0][6:57]
    return list(new_df.loc[new_obs, 'id'])


def feature_average(track_id):
    '''
    This function returns the sum of the features for the ten recommended songs.
    '''
    similar_tracks = predict_model(track_id)
    # Return a dataframe with only the ten most similar tracks
    similar_tracks = new_df[new_df["id"].isin(similar_tracks)]
    similar_tracks = similar_tracks[['acousticness', 'danceability',
                                     'energy', 'instrumentalness',
                                     'liveness',
                                     'speechiness', 'valence']]
    # Average features of ten tracks
    acousticness = round(similar_tracks['acousticness'].mean(), 2)
    danceability = round(similar_tracks['danceability'].mean(), 2)
    energy = round(similar_tracks['energy'].mean(), 2)
    instrumentalness = round(similar_tracks['instrumentalness'].mean(), 2)
    liveness = round(similar_tracks['liveness'].mean(), 2)
    #mode = round(similar_tracks['mode'].mean(), 2)
    speechiness = round(similar_tracks['speechiness'].mean(), 2)
    valence = round(similar_tracks['valence'].mean(), 2)
    # Store all to "features" variable
    features = []
    attributes = [
        acousticness,
        danceability,
        energy,
        instrumentalness,
        liveness,
        speechiness,
        valence]
    # features.append(acousticness)
    for attribute in attributes:
        features.append(attribute)
    return features


@router.get('/viz/{track_id}')
async def viz_fun(track_id: str):
    r = feature_average(track_id)
    attributes = [
        'acousticness',
        'danceability',
        'energy',
        'instrumentalness',
        'liveness',
        'speechiness',
        'valence']

    # Make Plotly figure
    fig = px.line_polar(r=r, theta=attributes, line_close=True)
    fig.update_traces(fill='toself')

    return fig.to_json(), fig.show()
