import os
from dotenv import load_dotenv
from os.path import join, dirname


# database file
dotenv_file = join(dirname(dirname(dirname(__file__))), '.env')
load_dotenv(dotenv_file)
DATABASE_URL = os.environ.get("DATABASE_URL")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
