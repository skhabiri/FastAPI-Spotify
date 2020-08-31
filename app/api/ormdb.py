"""
defines a class type for sqlalchemy, and loads the database based on a csv file
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


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Float
import csv
from .settings import DATABASE_URL
import psycopg2

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


class Songdb(Base):
    __tablename__ = "Song_table"
    """Song_db data model based on sqlalchemy 
    used by elephant postgres database """

    index = Column(Integer, primary_key=True, index=True)
    album = Column(String)
    aluri = Column(String(255), index=True)
    track_number = Column(Integer)
    trid = Column(String(255), index=True)
    name = Column(String(255))
    artist = Column(String)
    arid = Column(String(255), index=True)
    acousticness = Column(Float)
    danceability = Column(Float)
    energy = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    loudness = Column(Float)
    speechiness = Column(Float)
    tempo = Column(Float)
    valence = Column(Float)
    popularity = Column(Integer)


def reset_db(engine):
    """
    reset the database and re-create it
    """
    try:
        Base.metadata.drop_all(bind=engine)
    finally:
        Base.metadata.create_all(bind=engine)
    return


def get_db():
    """
    Open a db session
    """
    try:
        db.close()
    finally:
        db = SessionLocal()
        return db


def load_csv(db: Session, file_name: str):
    """
    Load a csv file into the db session
    """

    with open(file_name, "r") as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            db_record = Songdb(
                album=row["album"],
                aluri=row["aluri"],
                track_number=row["track_number"],
                trid =row["trid"],
                name=row["name"],
                artist=row["artist"],
                arid=row["arid"],
                acousticness=row["acousticness"],
                danceability=row["danceability"],
                energy=row["energy"],
                instrumentalness=row["instrumentalness"],
                liveness=row["liveness"],
                loudness=row["loudness"],
                speechiness=row["speechiness"],
                tempo=row["tempo"],
                valence=row["valence"],
                popularity=row["popularity"],
            )
            db.add(db_record)
        db.commit()
    return



