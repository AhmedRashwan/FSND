# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
import sys
from flask import (render_template,
                    request,
                    Response,
                    flash,
                    redirect,
                    url_for,
                    jsonify)
from flask_moment import Moment
import logging
from logging import (Formatter, FileHandler)
from flask_wtf import Form
from forms import *
from sqlalchemy import (or_, and_)
from models import (db, app, Venue, Artist, Show)
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#




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
    try:
        data = []
        # Get distinct venue depending on city and state
        venue_data = db.session.query(Venue).distinct(Venue.city).distinct(Venue.state).all()
        for elem in venue_data:
            venues = []
            # filter venues in depending city and state
            query = db.session.query(Venue).filter(and_(Venue.city==elem.city,Venue.state==elem.state)).all()
            for u in query:
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
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
        return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    try:
        error = False
        venue_count = db.session.query(Venue).filter(Venue.name.ilike('%'+request.form.get('search_term', '')+'%')).count()
        data=[]
        query = db.session.query(Venue).filter(Venue.name.ilike('%'+request.form.get('search_term', '')+'%')).all()
        for u in query:
            data.append({
              "id": u.id,
              "name": u.name,
              "num_upcoming_shows": 0,
            })
        response = {
          "count": venue_count,
          "data": data
        }
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if(error):
            flash('Sorry!! Venue ' + request.form.get('search_term') + ' could not be found.')
            return render_template('pages/home.html')
        else:
            return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        # -----------------------------------------------
        # @DONE prepare Past Shows and upcoming Shows
        # -----------------------------------------------
        past_shows_array = []
        upcoming_shows_array = []
        past_shows_query = db.session.query(Show, Venue, Artist).join(Venue, Artist).filter(Venue.id==venue_id, Show.show_time<=datetime.now()).all() 
        upcoming_shows_query = db.session.query(Show, Venue, Artist).join(Venue, Artist).filter(Venue.id==venue_id, Show.show_time>=datetime.now()).all()
        for p in past_shows_query:
            show = p[0]
            venue = p[1]
            artist = p[2]
            past_shows_array.append({
              "artist_id": artist.id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
            })
        for u in upcoming_shows_query:
            show = u[0]
            venue = u[1]
            artist = u[2]
            upcoming_shows_array.append({
              "artist_id": artist.id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
            })

        # -----------------------
        # @DONE Handle the Venue
        # -----------------------
        venue_data = db.session.query(Venue).get(venue_id)
        venue = {
            "id": venue_data.id,
            "name":venue_data.name,
            "genres": ((venue_data.genres).strip()).split(' '),
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
        data = list(filter(lambda d: d['id'] == venue_id, [venue]))[0]
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
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
  # --------------------------------------------------
  # @DONE Insert Data to DB
  # --------------------------------------------------
    try:
        error = False
        # --------------------------------------
        # @DONE Handle genres as space separated
        # -------------------------------------
        genres = ''
        for element in request.form.getlist('genres') :
            genres += element+' '

        new_venue = Venue(name=request.form.get('name'),
                          city=request.form.get('city'),
                          state=request.form.get('state'),
                          address=request.form.get('address'),
                          phone=request.form.get('phone'),
                          genres=genres,
                          facebook_link=request.form.get('facebook_link'),
                          image_link=request.form.get('image_link')
                          )
        db.session.add(new_venue)
        db.session.commit()
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
        error = True
    finally:
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
    try:
        error = False
        # ------------------------------------------------
        # @DONE Remove all show related to this venue
        # recuresivly before deleting the Venue
        # ------------------------------------------------
        venue = Venue.query.get(venue_id)
        shows = Show.query.filter_by(venue_id=venue_id).all() 
        for s in shows: 
            db.session.delete(s)

        db.session.delete(venue)  
        db.session.commit()
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
        error = True
    finally:
        # ------------------------------------------------
        # @DONE return aknowledge to the front End
        # ------------------------------------------------
        return jsonify({'success':not error})

#--------------------------------------------------
#  Artists
#  ------------------------------------------------
@app.route('/artists')
def artists():
    try:
        data = []
        query = db.session.query(Artist).all()
        for artist in query:
            data.append({
              'id': artist.id,
              'name': artist.name
            })     
    except Exception as e:
        print(sys.exc_info())  
        db.session.rollback()
    finally:
        db.session.close()
        return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    try:
        error = False
        data = []
        result_count = db.session.query(Artist).filter(Artist.name.ilike('%'+request.form.get('search_term', '')+'%')).count()
        query = db.session.query(Artist).filter(Artist.name.ilike('%'+request.form.get('search_term', '')+'%')).all()
        for artist in query:
            data.append({
                "id": artist.id,
                "name": artist.name,
            })
        response = {
        "count":result_count,
        "data": data
        }
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if(error):
            flash('Sorry!! Aritst ' + request.form.get('search_term') + ' could not be found.')
            return render_template('pages/home.html')
        else:
            return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    try:
        past_shows_array = []
        upcoming_shows_array = []
        artist_data = db.session.query(Artist).get(artist_id)
        past_shows_query = db.session.query(Show,Venue,Artist).join(Venue,Artist).filter(Artist.id==artist_id,Show.show_time<=datetime.now()).all() 
        upcoming_shows_query = db.session.query(Show,Venue,Artist).join(Venue,Artist).filter(Artist.id==artist_id,Show.show_time>=datetime.now()).all()

        for p in past_shows_query:
            show = p[0]
            venue = p[1]
            artist = p[2]
            past_shows_array.append({
              "venue_id": venue.id,
              "venue_name": venue.name,
              "venue_image_link": venue.image_link,
              "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
            })
        for u in upcoming_shows_query:
            show = u[0]
            venue = u[1]
            artist = u[2]
            upcoming_shows_array.append({
              "venue_id": venue.id,
              "venue_name": venue.name,
              "venue_image_link": venue.image_link,
              "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
            })
        artist = {
          "id": artist_data.id,
          "name":artist_data.name,
          "genres": ((artist_data.genres).strip()).split(' '),
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
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
        return render_template('pages/show_artist.html', artist=data)

# --------------------------------------
#  Update Artist
#  -------------------------------------
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
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        genres = ''
        for element in request.form.getlist('genres') :
            genres += element+' '

        artist = db.session.query(Artist).get(artist_id)
        artist.name=request.form.get('name')
        artist.genres= genres
        artist.city= request.form.get('city')
        artist.state= request.form.get('state')
        artist.phone=request.form.get('phone')
        artist.facebook_link= request.form.get('facebook_link')
        artist.image_link= request.form.get('image_link')
        db.session.add(artist)
        db.session.commit()
    except Exception as e:
        print(sys.exc_info())
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
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        genres = ''
        for element in request.form.getlist('genres') :
            genres += element+' '
        venue = db.session.query(Venue).get(venue_id)
        venue.name=request.form.get('name')
        venue.genres= genres
        venue.address= request.form.get('address')
        venue.city= request.form.get('city')
        venue.state= request.form.get('state')
        venue.phone=request.form.get('phone')
        venue.facebook_link= request.form.get('facebook_link')
        venue.image_link= request.form.get('image_link')
        db.session.add(venue)
        db.session.commit()
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()  
        return redirect(url_for('show_venue', venue_id=venue_id))

# -----------------
#  Create Artist
#  ----------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # ---------------------------
  # @DONE Insert Data to DB
  # ---------------------------
    try:
        error = False
        genres = ''
        for element in request.form.getlist('genres') :
            genres += element+' '

        new_artist = Artist(name=request.form.get('name'),
                          city=request.form.get('city'),
                          state=request.form.get('state'),
                          phone=request.form.get('phone'),
                          genres=genres,
                          facebook_link=request.form.get('facebook_link'),
                          image_link=request.form.get('image_link')
                          )
        db.session.add(new_artist)
        db.session.commit()
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
        error = True
    finally:
          # --------------------------------------------------
          # @DONE update error message
          # --------------------------------------------------
        db.session.close()
        if(error):
          flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        else:
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    try:
        data = []
        query = db.session.query(Show,Artist,Venue).join(Artist,Venue).all()
        for result in query:
          show = result[0]
          artist = result[1]
          venue = result[2]
          data.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": datetime.strftime(show.show_time,'%Y-%m-%d %H:%M:%S')
          })
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
        return render_template('pages/shows.html', shows=data)

# ---------------------------
#  CREATE A SHOW
# ---------------------------    
@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        error = True
        # -----------------------------------------------
        # @DONE Check first if venue and Artist is exist
        # -----------------------------------------------
        venue = db.session.query(Venue).get(request.form.get('venue_id'))
        artist = db.session.query(Artist).get(request.form.get('artist_id'))

        if venue is None or artist is None:
            error = True
        else:
            show = Show(
              artist_id=request.form.get('artist_id'),
              venue_id=request.form.get('venue_id'),
              show_time=request.form.get('start_time'),
              )
            db.session.add(show)
            db.session.commit()
            error=False
    except Exception as e:
        print(sys.exc_info())
        db.session.rollback()
        error = True
    finally:
        db.session.close()  
        if(error):
            flash('An error occurred. Show could not be listed.')
        else:
            flash('Show was successfully listed!')
        return render_template('pages/home.html')

# ---------------------------
# ERORR HANDLING
# --------------------------
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
