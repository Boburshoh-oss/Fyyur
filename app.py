#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
import logging
import datetime
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import os

#----------------------------------------------------------------------------#
# App Config.
from config import SQLALCHEMY_DATABASE_URI, DEBUG, SQLALCHEMY_TRACK_MODIFICATIONS
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
db.create_all()
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#----------------------------------------------------------------------------#
# Models.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(1000))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website =db.Column(db.String())
    genres=db.Column(ARRAY(db.String()))
    seeking_description=db.Column(db.String())
    seeking_talent=db.Column(db.String())

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue=db.Column(db.String())
    seeking_description=db.Column(db.String())
    website =db.Column(db.String())

class Show(db.Model):
      __tablename__='Show'
      id=db.Column(db.Integer,primary_key=True)
      start_time=db.Column(db.DateTime)
      venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
      venue_name=db.relationship('Venue',backref=db.backref('shows'))
      artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
      artist=db.relationship('Artist',backref=db.backref('shows'))
db.create_all()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  data=[]
  distincts=db.session.query(Venue.city, Venue.state).distinct(Venue.city,Venue.state)
  for item in distincts:
        vens=db.session.query(Venue.id,Venue.name).filter(Venue.city==item[0]).filter(Venue.state==item[1])
        data.append({
          'city':item[0],
          'state':item[1],
          'venues':vens
        })
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
      searchTerm=request.form.get('search_term','')
      venues=Venue.query.filter(Venue.name.ilike(f'%{searchTerm}%'))
      data=[]
      for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": [num for num in Show.query.filter_by(venue_id=venue.id) if num.start_time>datetime.now()]
          })
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
      print(data)
      response={
        "count": venues.count(),
        "data": data
      }
      
      return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=db.session.query(Venue).filter(Venue.id==venue_id).one()
  
  lists=db.session.query(Show).filter(Show.venue_id==venue_id)
  past=[]
  upcoming=[]
  
  for item in lists:
        artist=db.session.query(Artist.name,Artist.image_link)
        show_add={
          'artist_id':item.artist_id,
          'artist_name':artist.name,
          'artist_image_link':artist.image_link,
          'start_time':item.start_time.strftime('%m%d%Y')
        }
        if item.start_time<datetime.now():
              past.append(show_add)
        else:
            upcoming.append(show_add)
        
  data={
    "id": venue.id,
    "name": venue.name,
    "genres":venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website ,
    "facebook_link":venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":past,
    "upcoming_shows":upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website_link.data,
    facebook_link = form.facebook_link.data,
    seeking_talent = form.seeking_talent.data, 
    seeking_description = form.seeking_description.data,
    image_link = form.image_link.data,
  )
  db.session.add(venue)
  db.session.commit()
  db.session.close()
  flash('Venue ' + form.name.data + ' was successfully listed !')
  
  # try:
  #     db.session.add(venue)
  #     db.session.commit()
  #     flash('Venue ' + form.name.data + ' was successfully listed !')
  # except:
  #     flash('Sorry, an error occurred. Venue ' + form.name.data + ' could not be added.')
  # finally:
  #     db.session.close()
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
      form = VenueForm()
      venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
      return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
      
      form = VenueForm()
      # try:
      venue = Venue.query.get_or_404(venue_id)
      venue.name=form.name.data,
      venue.genres=form.genres.data,
      venue.address=form.address.data,
      venue.city=form.city.data,
      venue.state=form.state.data,
      venue.phone=form.phone.data,
      venue.website=form.website_link.data,
      venue.facebook_link=form.facebook_link.data,
      venue.seeking_talent=form.seeking_talent.data,
      venue.seeking_description=form.seeking_description.data,
      venue.image_link=form.image_link.data
    
    
      db.session.commit()
    
      flash('Venue' + form.name.data + ' was successfully updated !')
      # except:
      #     flash('Sorry, an error occurred. Venue ' + form.name.data + ' could not be updated.')
      #     print(sys.exc_info())
      # finally:
      #     db.session.close()
      return redirect(url_for('show_venue', venue_id=venue_id))
#  ----------------------------------------------------------------



@app.route('/venues/<int:venue_id>del', methods=['DELETE'])
def delete_venue(venue_id):
      db.session.query(Show).filter(Show.venue_id==venue_id).delete()
      db.session.query(Venue).filter(Venue.id==venue_id).delete()
      db.session.commit()
      flash('Venue was  deleted')
      
      db.session.close()
          
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
      return redirect(url_for('venues'))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
      artists=db.session.query(Artist.id,Artist.name)
      data=[]
      for i in artists:
            data.append({
              'id':i[0],
              'name':i[1]
            })
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
      return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
      searchTerm=request.form.get('search_term','')
      artists=db.session.query(Artist).filter(Artist.name.ilike('%'+searchTerm+'%')).all()
      data=[]
      
      for item in artists:
            num_upcoming_shows=0
            shows=db.session.query(Show).filter(Show.artist_id==item.id)
            for show in shows:
                  if show.start_time>datetime.now():
                        num_upcoming_shows+=1
            data.append({
              'id':item.id,
              'name':item.name,
              'num_upcoming_shows':num_upcoming_shows
            })
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
            response={
              "count": len(artists),
              "data": data
            }
            return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
      artist=Artist.query.get_or_404(artist_id)
      lists=db.session.query(Show).filter(Show.artist_id==artist_id)
      past=[]
      upcoming=[]
      
      for i in lists:
            venue=db.session.query(Venue.name,Venue.image_link).filter(Venue.id==i.venue_id).one()
            
            add={
              'venue_id':i.venue_id,
              'venue_name':venue.name,
              'venue_image_link':venue.image_link,
              'start_time':i.start_time.strftime('%m/%d/%Y')
            }
            if i.start_time<datetime.now():
                  past.append(add)
            else:
                  print(add,file=sys.stderr)
                  upcoming.append(add)
            

            
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
      data={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website ,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past,
        "upcoming_shows": upcoming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
      }


      # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
      return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get_or_404(artist_id)
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
      form=ArtistForm(request.form)
      updated_artist={
        'name':form.name.data,
        'genres':form.genres.data,
        'city':form.city.data,
        'state':form.state.data,
        'phone':form.phone.data,
        'website':form.website_link.data,
        'facebook_link':form.facebook_link.data,
        'seeking_venue':form.seeking_venue.data,
        'seeking_description':form.seeking_description.data,
        'image_link':form.image_link.data
      }
      db.session.query(Artist).filter(Artist.id==artist_id).update(updated_artist)
      try:
        db.session.commit()
        flash('Artist '+form.name.data+' was successfully listed !')
      except:
          flash('Sorry, an error occurred. Artist '+form.name.data+' could not be added')
      finally:
        db.session.close()
      
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>/del', methods=['GET', 'DELETE'])
def delete_artist(artist_id):
      try:
        
        db.session.query(Show).filter(Show.artist_id == artist_id).delete()
        db.session.query(Artist).filter(Artist.id == artist_id).delete()
        db.session.commit()
        flash('Artist was successfully deleted!')
      except:
          flash('Sorry, an error occurred. The  Venue you selected cannot be deleted..')
      finally:
          db.session.close()
      return redirect(url_for('artists'))





#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
      form=ArtistForm(request.form)
      
      artist=Artist(
        name=form.name.data,
        genres=form.genres.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        website=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_description=form.seeking_description.data,
        image_link=form.image_link.data
      )
      try:
        db.session.add(artist)
        db.session.commit()
        flash('Artist '+form.name.data+' was successfully list!')
        
      except:
        flash('Artist '+form.name.data+' was successfully list')
      finally:
        db.session.close()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[]
  shows=db.session.query(Show.artist_id,Show.venue_id,Show.start_time,Show.id).all()
  
  for i in shows:
        artist=db.session.query(Artist.name,Artist.image_link).filter(Artist.id==i[0]).one()
        venue=db.session.query(Venue.name).filter(Venue.id==i[0]).one()
        data.append({
          'show_id':i[3],
          'venue_id':i[1],
          'venue_name':venue[0],
          'artist_id':i[0],
          'artist_name':artist[0],
          'artist_image_link':artist[1],
          'start_time':str(i[2])
        })
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  artist=db.session.query(Artist.id,Artist.name)
  listArtist=[]
  for i in artist:
        listArtist.append((int(i[0]),'(id: '+str(i[0])+'),Name: ' + str(i[1])))
  
  form.artist_id.choices=listArtist
  venues=db.session.query(Venue.id,Venue.name)
  listVenues=[]
  for i in venues:
        listVenues.append((int(i[0]),'(id: ' + str(i[0]) + '), Name: ' + str(i[1])))
  form.venue_id.choices=listVenues
  
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form=ShowForm(request.form)
  
  show=Show(
    venue_id=form.venue_id.data,
    artist_id=form.artist_id.data,
    start_time=form.start_time.data
  )
  
  try:
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully placed')
  except:
    flash('Sorry, an error occurred. Show could not be listed')
  finally:
    db.session.close()
    
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/shows/<show_id>/del', methods=['GET'])
def delete_show(show_id):
      
      try:
          db.session.query(Show).filter(Show.id == show_id).delete()
          db.session.commit()
          flash('Show was successfully deleted!')
      except:
          flash('Sorry, an error occurred. Show could not be deleted.')
      finally:
          db.session.close()
      return redirect(url_for('shows'))
    

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
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port,debug=DEBUG)

