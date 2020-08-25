import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database



# ---------------------------------------
# @DONE add a connection parameters
# ---------------------------------------
DIALECT = 'postgres'
DBNAME = 'fyyurTest4'
DB_USER = 'postgres'
DB_PASSWORD = 'password'
PORT = 5432
HOST = 'localhost'

SQLALCHEMY_DATABASE_URI = f'{DIALECT}://{DB_USER}:{DB_PASSWORD}@{HOST}:{PORT}/{DBNAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False