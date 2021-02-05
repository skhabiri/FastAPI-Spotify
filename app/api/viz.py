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


import pandas as pd
import plotly.graph_objects as go
from app.api.predict import predict_model, df, knn, router


def feature_average(track_id):
    '''
    This function returns the sum of the features for the ten recommended songs.
    '''
    similar_tracks = predict_model(track_id, df, knn)
    
    # Return a dataframe with only the most similar tracks
    similar_tracks = df[df["id"].isin(similar_tracks)]
    
    attributes = [
        "acousticness",
        "danceability",
        "energy",
        "instrumentalness",
        "liveness",
        "speechiness",
        "valence"]

    similar_tracks = similar_tracks[attributes]

    features = []
    for attribute in attributes:
        # Average features of the similar tracks
        features.append(round(similar_tracks[attribute].mean(), 2))

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
    
    rid = (df[df["id"]==track_id][attributes].values.round(3)).tolist()[0]

    # Make Plotly figure
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=r, theta=attributes, fill='toself', name='Suggestion'))
    
    fig.add_trace(go.Scatterpolar(
        r=rid, theta=attributes, fill='toself', name='Query'))   

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)), showlegend=True)

    return fig.to_json(), fig.show()
