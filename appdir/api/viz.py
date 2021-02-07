"""
Radar plot of audio features for a trackId
"""

print("\n__file__: {}".format(__file__))
if __name__ == '__main__' and  __package__ is None:
    print("is running as a Python Script")
else:
    print("is running as a Python Module")

print("__name__ is: {}".format(__name__))
print("__package__ is: {}".format(__package__))

# None is for script and "" is for python repl import module
if __package__ in [None, ""]:
    # adding project directory to the path 
    import re
    # remove the "/filename.py"
    c_dir = re.sub(r"(^.*)\/.*\.py$", r"\g<1>", __file__)
    
    from sys import path
    from os.path import dirname as dir
    print("existing path:\n", path)

    path.append(dir(dir(c_dir)))   
    # now everything under FastAPI-Spotify, including "appdir" would be recognized

    print("expanded system path:\n", path)
    __package__ = "appdir.api"


import pandas as pd
import plotly.graph_objects as go
from appdir.api.predict import predict_model, df, knn, router
from fastapi import HTTPException

def feature_average(track_id):
    '''
    This function returns the sum of the features for the ten recommended songs.
    '''
    try:
        similar_tracks = predict_model(track_id, df, knn)
    except Exception as e:
        print(e.args)
        raise HTTPException(status_code=500, detail="Input is not in the trained dataset")
    
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
async def viz_func(track_id: str):
    
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
