"""
defines the front end data model type for use in fastapi
"""
# import logging
# from fastapi import APIRouter
import pandas as pd
from pydantic import BaseModel, Field, validator


# pydantic Schema for Fastapi front end
class Song(BaseModel):
    """Front end data model used by fastapi"""
    album: str
    aluri: str
    track_number: int
    trid: str
    name: str
    artist: str
    arid: str
    acousticness: float = Field(..., example=0.029400)
    energy: float = Field(..., example=0.579)
    danceability: float
    instrumentalness: float
    liveness: float
    loudness: float
    speechiness: float
    tempo: float
    valence: float
    popularity: int

    class Config:
        orm_mode = True


# song of type Song
def to_df(song: Song):
    """Convert pydantic object to pandas dataframe with 1 row."""
    return pd.DataFrame([dict(song)])


