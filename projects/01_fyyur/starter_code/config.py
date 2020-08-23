import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# ---------------------------------------
# @DONE add a connection parameters
# ---------------------------------------
dialect = 'postgres'
db_name = 'fyyur'
db_username = 'postgres'
db_password = 'password'
port = 5432
host = 'localhost'

SQLALCHEMY_DATABASE_URI = f'{dialect}://{db_username}:{db_password}@{host}/{db_name}'
SQLALCHEMY_TRACK_MODIFICATIONS = False