"""
Spotify app based on fastapi
routs:
/: root

/predict/{id}: Gets a track id and returns a list of suggestions based on a joblib knn model

/viz/{track_id}: Plots a radar plot of audio features of a trackId

/Track_Search: Search Spotify for a phrase and returns a limited
list of artists, albums and track names

/Create_csv: generate csv file containing information of all tracks
 derived from a phrase search on Spotify

/DB_Load: Reset and Load the csv file into elephant postgress database

/DB_Query: returns the first 20 tracks from database

/DB_Reset: Reset the database

/README: Renders README.md


To launch the local web server on terminal:
uvicorn app.main:app --reload
"""

if __name__ == '__main__' and  __package__ is None:
    print("__name__ is: {}".format(__name__))
    print("__package__ is: {}".format(__package__))
    print("__file__ is: {}".format(__file__))
    __package__ = "app"
else:
    print("__name__ is: {}".format(__name__))
    print("__package__ is: {}".format(__package__))
    print("__file__ is: {}".format(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .api.settings import *
from typing import List, Optional, Set, TypeVar
from .api import fedata, predict, viz, parser, ormdb
# from .api.fedata import Song
# from .api.predict import *
# from .api.viz import *
# from .api.parser import *


app = FastAPI(
    title='Spotify Web App',
    description='Fast-API interface for Spotify application',
    version='0.1',
    docs_url='/',
)


app.include_router(predict.router)
app.include_router(viz.router)
# app.include_router(parser.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/")
def root():
    """
    Lists all the routs
    """
    return "See the README.md"


@app.post('/Track_Search/')
def songsearch(phrase: str):
    """
    An API call to Spotify, to search for a
    keyword and return a list of dictionaries
    containing the artist, album and track names
    ex/ key_word = {"california dreamin"}
    :return:
    """
    return parser.spotify_parser(phrase)


@app.post("/Create_csv/")
def csvgen(phrase: str):
    """
    Search spotify api and save all the album tracks related
    to the keyword in 'spotify_music.csv'. The data is also
    returned as original dictionary (json) format.
    """
    file_name = "./spotify_music.csv"
    return parser.create_csv(phrase, file_name)


@app.get("/DB_Load")
def db_reload():
    """
    Reset and reload the database from spotify_music.csv file
    """
    ormdb.reset_db(ormdb.engine)
    db = ormdb.get_db()
    file_name = "./spotify_music.csv"
    ormdb.load_csv(db, file_name)
    songs = db.query(ormdb.Songdb).all()
    db.close()

    return f"{len(songs)} records loaded"


@app.get("/DB_Query/", response_model=List[fedata.Song])
def query_tracks():
    """
    Get the first 20 tracks that exist in the database.
    """
    db = ormdb.get_db()
    songs = db.query(ormdb.Songdb).limit(20).all()
    db.close()
    return songs


@app.post("/DB_Reset")
def reset():
    """
    Flush the database
    """
    ormdb.reset_db(ormdb.engine)
    return "Database reset!"


@app.get("/README")
def readmedoc():
    """
    # Data Science Build Week [[  Final DRAFT  ]]
    Data Set: Kaggle Spotify Dataset 1912-2020, 160k Tracks

    Model Type: K-nearest neighbors

    Target: Song ID’s

    #### Teams
    - DS_16 Machine Learning
    - DS_17 Data Engineering


    Content:
    - [Product Vision](#product-vision)
    - [Tech Stack](#tech-stack)
    - [Project Goals](#project-goals)
    - [Audio Features](#audio-features)
    - [Getting started](#getting-started)
    - [File Structure](#file-structure)
    - [More Instructions](#more-instructions)
    - [Deploying to Heroku](#deploying-to-heroku)
    - [Example: Data Visualization](#example-data-visualization)
    - [Example: Machine Learning](#example-machine-learning)
    - [Color Scheme](#color-scheme)

    ## Product Vision

    To build a functioning application programming interface and machine learning model to be used in a full-stack enviroment capable of recieving front-end GET requests and outputting POST requests to back-end.

    ## Tech stack
    - [FastAPI](https://fastapi.tiangolo.com/): Web framework. Like Flask, but faster, with automatic interactive docs.
    - [Flake8](https://flake8.pycqa.org/en/latest/): Linter, enforces PEP8 style guide.
    - [Heroku](https://devcenter.heroku.com/): Platform as a service, hosts your API.
    - [Pipenv](https://pipenv.pypa.io/en/latest/): Reproducible virtual environment, manages dependencies.
    - [Plotly](https://plotly.com/python/): Visualization library, for Python & JavaScript.
    - [Pytest](https://docs.pytest.org/en/stable/): Testing framework, runs your unit tests.
    - [Uvicorn](https://www.uvicorn.org/#quickstart): Uvicorn is a lightning-fast ASGI server, built on uvloop and httptools.
    - [SQLAlchemy](https://www.sqlalchemy.org/): SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
    - [Spotipy](https://spotipy.readthedocs.io/en/2.13.0/): (Not designed in structure of project) Spotipy is a lightweight Python library for the Spotify Web API. With Spotipy you get full access to all of the music data provided by the Spotify platform.
    - [SciKit-Learn](https://scikit-learn.org/stable/getting_started.html): Simple and efficient tools for predictive data analysis.
    - [Pandas](https://pandas.pydata.org/docs/getting_started/index.html): Pandas is an open source, BSD-licensed library providing high-performance, easy-to-use data structures and data analysis tools for the Python programming language.

    ## Project Goals

    Describe the established data source with at least rough data able to be provided on day one.

    A: List of songs, basic info about songs, song name, artist, album, length of song, genre, general classification/categorization, number of plays, indicator of how much you might like song

    Write a description for what the data science problem is. Discover an uncertainty and/or a prediction. Use the data to find a solution to this problem.

    A: The Data Science team aims to solve the problem of inadequate or inaccurate predictions of songs that the user might enjoy. Current models do not seem to be super effective -- a large portion of our team does not enjoy ~30% of their Discovery Weekly playlist, and we aim to minimize that number (aiming for ~20%)

    Create a good song suggestion. Determine how we know the suggestion was good. Determine whether the user would like it or add it to playlist of any kind.

    A: From our team's personal experience, listening to a song all the way through without skipping is generally the best indication of whether a song was a good prediction or not. Adding a song to a playlist or liking a song can give an indication about a particularly good suggestion, but we've discovered that most users are not likely to do this on "good suggestions" only "really good suggestions".

    Determine the targeted output to deliver to the Web/UX/iOS teams. Ensure JSON format or requested output format is used.

    A: The Spotify API already outputs search requests as JSON, which our Data Engineer plans to flatten for ease of data analysis. We plan to change this back to Python via a Flask app when we return it to the backend team.

    ## Audio Features

    - Acoustics (Confidence levels ranging from 0.0 to 1.0. 1.0 represents high confidence the track is acoustic.)

    - Artist Popularity (A value between 0 and 100, with 100 being the most popular. The popularity is calculated by algorithm and is based, in the most part, on the total number of plays the track has had and how recent those plays are.)

    - Danceability (Confidence levels ranging from 0.0 to 1.0. 1.0 represents track is most danceable based on tempo, rhythm stability, beat strength, and overall regularity.)

    - Duration_MS (The duration of the track in milliseconds.)

    - Energy (Confidence levels ranging from 0.0 to 1.0 representing a measure of intensity and activity. For example, acid screamo has high energy whereas trance scores low on the scale.)

    - Instrumentalness (Confidence levels ranging from 0.0 to 1.0. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. - Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0. “Ooh” and “aah” sounds are treated as instrumental in this context.)

    - Genre (* A conventional category that identifies some pieces of music as belonging to a shared tradition or set of conventions. It is to be distinguished from musical form and musical style.)

    - ID (A string to uniquely identify the Spotify ID for a track. For example, '1kKLWkqyZEnrOd5tBYYCUn',)

    - Liveness (Confidence levels ranging from 0.0 to 1.0. A value above 0.8 provides confidence the track is live.)

    - Loudness (Amplitude level ranging from -60 to 0 decibels (dB).)

    - Mode (Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.)

    - Speechiness (Confidence levels ranging from 0.0 to 1.0 to detect the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. podcast, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.)

    - Tempo (The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.)

    - URI (A string to uniquely identify the Spotify URI (Uniform Resource Identifier) for a track. For example, 'spotify:track:7lEptt4wbM0yJTvSG5EBof':
    https://itknowledgeexchange.techtarget.com/overheard/files/2016/11/URI.png.)

    - Year (Production year of a track.)


    Reason for using K-nearest neighbors: We chose to work with nearest neighbors because of its ability to cluster observations around common features. Since we were working a tabular dataset it seemed best to avoid any type of neural networks. There was also no need to apply any NLP techniques because there was justifiable reason to use it on any of the columns that contained text. Instead we dummy encoded the genres because most songs had multiple genres/sub genres.

    Results:  We were able to pull an array of similar song suggestions when we would input a single song ID.

    Further research: We have begun working on applying text classification to the lyrics of the songs to see if we can get a different type of recommendation that is still useful and appreciated by the user.

    * Spotify Kaggle Dataset: https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks
    * Spotify Audio Features: https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/
    * Genre definition: https://en.wikipedia.org/wiki/Music_genre

    ## Big Picture

    Here's a template with starter code to deploy an API for your machine learning model and data visualizations.

    You can deploy on Heroku in 10 minutes. Here's the template deployed as-is: [https://ds-bw-test.herokuapp.com/](https://ds-bw-test.herokuapp.com/)

    This diagram shows two different ways to use frameworks like Flask.

    ![](https://user-images.githubusercontent.com/7278219/87967396-5a6fed80-ca84-11ea-902a-890cfa6115d3.png)

    Instead of Flask, use FastAPI. It's similar, but faster, with automatic interactive docs. For more comparison, see [FastAPI for Flask Users](https://amitness.com/2020/06/fastapi-vs-flask/).

    Build and deploy a Data Science API. May need to work cross-functionally with a Web teammate to connect the API to a full-stack web app!

    ![](https://user-images.githubusercontent.com/7278219/87967579-a4f16a00-ca84-11ea-9f90-886b3cf1a25c.png)

    ## Getting Started

    [Create a new repository from this template.](https://github.com/Lambda-School-Labs/ds-bw/generate)

    Clone the repo
    ```
    git clone https://github.com/YOUR-GITHUB-USERNAME/YOUR-REPO-NAME.git

    cd YOUR-REPO-NAME
    ```

    Install dependencies
    ```
    pipenv install --dev
    ```

    Activate the virtual environment
    ```
    pipenv shell
    ```

    Launch the app
    ```
    uvicorn app.main:app --reload
    ```

    Go to `localhost:8000` in the browser.

    """
    return


if __name__ == '__main__':
    uvicorn.run(app)
