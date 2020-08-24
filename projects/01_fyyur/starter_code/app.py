#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import or_,and_

# ------------------------------------------------
# @DONE add Migrate Class
# ------------------------------------------------
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
# ------------------------------------------------
# @DONE add migration instance
# ------------------------------------------------
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# -------------------------------------------------
# @DONE implement relation between Venue and Artist
# ------------------------------------------------
venue_artists = db.Table('venue_artists',
                db.Column('venue_id',db.Integer,db.ForeignKey('Venue.id')),
                db.Column('artist_id',db.Integer,db.ForeignKey('Artist.id')))

           

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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # TODO: DONE 
    # --------------------------------------------
    # @DONE implement add columns artist model
    # -------------------------------------------
    genres = db.Column(db.String(120))
    venue_shows = db.relationship('Show',backref='venue_shows',lazy=True)

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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    # --------------------------------------------
    # @DONE implement add columns artist model
    # -------------------------------------------
    artist_shows = db.relationship('Show',backref='artist_shows',lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------
# @DONE implement Show Model
# ----------------------------
class Show(db.Model):
  __tablename__ = "Show"
  id = db.Column(db.Integer,primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
  show_time = db.Column(db.DateTime,nullable=True)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  try:
    data = []
    # Get distinct venue depending on city and state
    venue_data = db.session.query(Venue).distinct(Venue.city).distinct(Venue.state).all()
    for elem in venue_data:
      venues= []
      # filter venues in depending city and state
      for u in  db.session.query(Venue).filter(and_(Venue.city==elem.city,Venue.state==elem.state)).all():
        venues.append({
          'id': u.id,
          'name': u.name,
          'num_upcoming_shows': 0,
        })
      data.append({
        'city' : elem.city,
        'state': elem.state,
        'venues': venues
      })
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  try:
    venue_count = db.session.query(Venue).filter(Venue.name.ilike('%'+request.form.get('search_term', '')+'%')).count()
    data=[]
    for u in db.session.query(Venue).filter(Venue.name.ilike('%'+request.form.get('search_term', '')+'%')).all():
        data.append({
          "id": u.id,
          "name": u.name,
          "num_upcoming_shows": 0,
        })
    response={
      "count": venue_count,
      "data": data
    }
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    past_shows_array = []
    upcoming_shows_array = []
    venue_data = db.session.query(Venue).get(venue_id)
    past_shows_query = db.session.query(Show,Venue,Artist).join(Venue,Artist).filter(Venue.id==venue_id,Show.show_time<=datetime.now()).all() 
    upcoming_shows_query = db.session.query(Show,Venue,Artist).join(Venue,Artist).filter(Venue.id==venue_id,Show.show_time>=datetime.now()).all()

    for p in past_shows_query:
      print(p)
      show    = p[0]
      venue   = p[1]
      artist  = p[2]
      past_shows_array.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
      })
    for u in upcoming_shows_query:
      show    = u[0]
      venue   = u[1]
      artist  = u[2]
      upcoming_shows_array.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
      })

    venue={
      "id": venue_data.id,
      "name":venue_data.name,
      "genres": venue_data.genres,
      "address": venue_data.address,
      "city": venue_data.city,
      "state": venue_data.state,
      "phone":venue_data.phone,
      "website": "https://www.themusicalhop.com",
      "facebook_link": venue_data.facebook_link,
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": venue_data.image_link,
      "past_shows": past_shows_array,
      "upcoming_shows": upcoming_shows_array,
      "past_shows_count": len(past_shows_array),
      "upcoming_shows_count": len(upcoming_shows_array),
    }
    print(venue)
    data = list(filter(lambda d: d['id'] == venue_id, [venue]))[0]
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # --------------------------------------------------
  # @DONE Insert Data to DB
  # --------------------------------------------------
  try:
    error = False
    new_venue = Venue(name=request.form.get('name'),
                      city=request.form.get('city'),
                      state=request.form.get('state'),
                      address=request.form.get('address'),
                      phone=request.form.get('phone'),
                      genres=request.form.get('genres'),
                      facebook_link=request.form.get('facebook_link')
                      )
    db.session.add(new_venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., 
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

      # --------------------------------------------------
      # @DONE update error message
      # --------------------------------------------------
    db.session.close()
    if(error):
      flash('An error occurred. Venue ' +  request.form.get('name') + ' could not be listed.')
    else:
      flash('Venue ' + request.form.get('name') + ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    error = False
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all() 
    for s in shows: 
      db.session.delete(s)
    db.session.delete(venue)  
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
    error = True
  finally:
    return jsonify({'success':not error})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  try:
    data = []
    # TODO: replace with real data returned from querying the database
    for artist in db.session.query(Artist).all():
      data.append({
        'id': artist.id,
        'name': artist.name
      })     
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  try:
    data = []
    result_count = db.session.query(Artist).filter(Artist.name.ilike('%'+request.form.get('search_term', '')+'%')).count()
    for artist in db.session.query(Artist).filter(Artist.name.ilike('%'+request.form.get('search_term', '')+'%')).all():
      data.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": 0,
      })
    response={
    "count":result_count,
    "data": data
    }
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    past_shows_array = []
    upcoming_shows_array = []
    artist_data = db.session.query(Artist).get(artist_id)
    past_shows_query = db.session.query(Show,Venue,Artist).join(Venue,Artist).filter(Artist.id==artist_id,Show.show_time<=datetime.now()).all() 
    upcoming_shows_query = db.session.query(Show,Venue,Artist).join(Venue,Artist).filter(Artist.id==artist_id,Show.show_time>=datetime.now()).all()

    for p in past_shows_query:
      show    = p[0]
      venue   = p[1]
      artist  = p[2]
      past_shows_array.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
      })
    for u in upcoming_shows_query:
      show    = u[0]
      venue   = u[1]
      artist  = u[2]
      upcoming_shows_array.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
      })
    artist={
      "id": artist_data.id,
      "name":artist_data.name,
      "genres": artist_data.genres,
      "city": artist_data.city,
      "state": artist_data.state,
      "phone":artist_data.phone,
      "website": "https://www.themusicalhop.com",
      "facebook_link": artist_data.facebook_link,
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": artist_data.image_link,
      "past_shows": past_shows_array,
      "upcoming_shows":upcoming_shows_array,
      "past_shows_count": len(past_shows_array),
      "upcoming_shows_count": len(upcoming_shows_array),
    }
    data = list(filter(lambda d: d['id'] == artist_id, [artist]))[0]
  except Exception as e:
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_data = db.session.query(Artist).get(artist_id)
  artist={
    "id": artist_data.id,
    "name": artist_data.name,
    "genres": artist_data.genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artist_data.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = db.session.query(Artist).get(artist_id)
    artist.name=request.form.get('name')
    artist.genres= request.form.get('genres')
    artist.city= request.form.get('city')
    artist.state= request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.facebook_link= request.form.get('facebook_link')
    artist.image_link= request.form.get('image_link')
    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()  
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = db.session.query(Venue).get(venue_id)
  venue={
    "id": venue_data.id,
    "name":venue_data.name,
    "genres": venue_data.genres,
    "address": venue_data.address,
    "city": venue_data.city,
    "state": venue_data.state,
    "phone":venue_data.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venue_data.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = db.session.query(Venue).get(venue_id)
    venue.name=request.form.get('name'),
    venue.genres= request.form.get('genres'),
    venue.address= request.form.get('address'),
    venue.city= request.form.get('city'),
    venue.state= request.form.get('state'),
    venue.phone=request.form.get('phone'),
    venue.facebook_link= request.form.get('facebook_link'),
    venue.image_link= request.form.get('image_link')
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()  
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
 # --------------------------------------------------
  # @DONE Insert Data to DB
  # --------------------------------------------------
  try:
    error = False
    new_artist = Artist(name=request.form.get('name'),
                      city=request.form.get('city'),
                      state=request.form.get('state'),
                      phone=request.form.get('phone'),
                      genres=request.form.get('genres'),
                      facebook_link=request.form.get('facebook_link')
                      )
    db.session.add(new_artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., 
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

      # --------------------------------------------------
      # @DONE update error message
      # --------------------------------------------------
    db.session.close()
    if(error):
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  try:
    data = []
    query = db.session.query(Show,Artist,Venue).join(Artist,Venue).all()
    print(query)
    for result in query:
      show   = result[0]
      artist = result[1]
      venue  = result[2]
      data.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": "2035-04-08T20:00:00.000Z"
      })
  except Exception as e:
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
    return render_template('pages/shows.html', shows=data)
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    error = False
    show = Show(
      artist_id=request.form.get('artist_id'),
      venue_id=request.form.get('venue_id'),
      show_time=request.form.get('start_time'),
      )
    print(show.show_time)

    db.session.add(show)
    db.session.commit()
    error=False
  except expression as e:
    db.session.rollback()
    print(e)
    error = True
  finally:
    db.session.close()  
    if(error):
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
