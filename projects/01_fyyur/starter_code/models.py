from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from flask_moment import Moment

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# -------------------------------------------------
# @DONE implement relation between Venue and Artist
# ------------------------------------------------
venue_artists = db.Table('venue_artists',
                db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id')),
                db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id')))


# -----------------
# VENUE MODEL
# -----------------
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # --------------------------------------------
    # @DONE implement add columns artist model
    # -------------------------------------------
    genres = db.Column(db.String(120))
    venue_shows = db.relationship('Show', backref='venue_shows', lazy=True)


# ----------------------
# ARTIST MODEL
# -----------------------
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))    
    # --------------------------------------------
    # @DONE implement add columns artist model
    # -------------------------------------------
    artist_shows = db.relationship('Show', backref='artist_shows', lazy=True)

# ----------------------------
# @DONE implement Show Model
# ----------------------------
class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    show_time = db.Column(db.DateTime, nullable=True)