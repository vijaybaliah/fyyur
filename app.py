# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import logging
import sys
from datetime import datetime
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from sqlalchemy import MetaData

from forms import VenueForm, ArtistForm, ShowForm

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), unique=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id}, {self.name}, {self.city}, {self.state},\
                {self.address}, {self.phone}, {self.genres},\
                {self.image_link}, {self.facebook_link},\
                {self.seeking_talent}, {self.seeking_description}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), unique=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id}, {self.name}, {self.city}, {self.state},\
                {self.phone}, {self.genres}, {self.image_link},\
                {self.facebook_link}, {self.seeking_venue},\
                {self.seeking_description}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),
                          nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),
                         nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show artist_id: {self.artist_id} venue_id: {self.venue_id}\
             start_time: {self.start_time} venue: {self.venue.name}>'

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming
    # shows per venue.
    # state_city_query = db.session.query(Venue.state, Venue.city).group_by(Venue.state, Venue.city).subquery()

    # venues_list = Venue.query.join(state_city_query, Venue.city == state_city_query.c.city)\
    # .order_by(Venue.city, Venue.state).all()

    venues_list = Venue.query.order_by(Venue.city, Venue.state).all()
    data = []
    city_state = ''
    for venue in venues_list:
        if city_state == venue.city + venue.state:
            data[len(data) - 1]['venues'].append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': 0
            })
        else:
            data.append({
                'city': venue.city,
                'state': venue.state,
                'venues': [{
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': 0
                }]
            })
            city_state = venue.city + venue.state
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string
    # search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop"
    # and "Park Square Live Music & Coffee"
    response = {}
    try:
        venue_list = Venue.query.with_entities(Venue.id, Venue.name).\
            filter(Venue.name.ilike('%' + request.form.get('search_term', '') +
                                    '%')).all()

        response['data'] = venue_list
        response['count'] = len(venue_list)
    except Exception as e:
        print(e)
        flash('An error occurred for the search term' +
              request.form.get('search_term', ''))
    finally:
        return render_template('pages/search_venues.html', results=response,
                               search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    setattr(venue, 'past_shows', [])
    setattr(venue, 'upcoming_shows', [])
    current_time = datetime.now()
    past_shows_count = 0
    upcoming_shows_count = 0
    shows = db.session.query(Artist, Show.start_time).join(Show).filter(Show.venue_id == venue_id)
    for artist, start_time in shows:
        if start_time < current_time:
            venue.past_shows.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': str(start_time)
            })
            past_shows_count += 1
        else:
            venue.upcoming_shows.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': str(start_time)
            })
            upcoming_shows_count += 1
    setattr(venue, 'past_shows_count', past_shows_count)
    setattr(venue, 'upcoming_shows_count', upcoming_shows_count)
    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    error = False
    try:
        if form.validate_on_submit():
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                address=form.address.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                website=form.website.data,
                facebook_link=form.facebook_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(venue)
            db.session.commit()
            # TODO: insert form data as a new Venue record in the db, instead
            # TODO: modify data to be the data object returned from db
            # insertion
        else:
            raise Exception('Form validation failed')
    except Exception as e:
        print('create_venue_submission: ', e)
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
        # on successful db insert, flash success
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be
        # listed.')
        flash('An error occurred. Venue '
              + request.form['name'] +
              ' could not be listed.')
        return render_template('forms/new_venue.html', form=form)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    # TODO: replace with real data returned from querying the database
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search.
    # Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and
    # "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {}
    try:
        artist_list = Artist.query.with_entities(Artist.id, Artist.name).\
            filter(Artist.name.ilike('%' + request.form.get('search_term', '')
                                     + '%')).all()

        response['data'] = artist_list
        response['count'] = len(artist_list)
    except Exception as e:
        print(e)
        flash('An error occurred for the search term' +
              request.form.get('search_term', ''))
    finally:
        return render_template('pages/search_artists.html', results=response,
                               search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    current_time = datetime.now()
    artist = Artist.query.get(artist_id)
    setattr(artist, 'past_shows', [])
    setattr(artist, 'upcoming_shows', [])
    past_shows_count = 0
    upcoming_shows_count = 0
    shows = db.session.query(Venue, Show.start_time).join(Show).filter(Show.artist_id == artist_id)
    for venue, start_time in shows:
        if start_time < current_time:
            artist.past_shows.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': str(start_time)
            })
            past_shows_count += 1
        else:
            artist.upcoming_shows.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': str(start_time)
            })
            upcoming_shows_count += 1
    setattr(artist, 'past_shows_count', past_shows_count)
    setattr(artist, 'upcoming_shows_count', upcoming_shows_count)

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(
        name=artist.name,
        genres=artist.genres,
        city=artist.city,
        state=artist.state,
        phone=artist.phone,
        website=artist.website,
        facebook_link=artist.facebook_link,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description,
        image_link=artist.image_link
    )
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    error = False
    try:
        if form.validate_on_submit():
            artist.name = form.name.data
            artist.genres = form.genres.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.website = form.website.data
            artist.facebook_link = form.facebook_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data
            db.session.add(artist)
            db.session.commit()
        else:
            raise Exception('Form validation failed')
    except Exception as e:
        print('edit_artist_submission: ', e)
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
        return redirect(url_for('show_artist', artist_id=artist_id))
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(
        name=venue.name,
        genres=venue.genres,
        address=venue.address,
        city=venue.city,
        state=venue.state,
        phone=venue.phone,
        website=venue.website,
        facebook_link=venue.facebook_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description,
        image_link=venue.image_link,
    )
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    form = VenueForm()
    error = False
    try:
        if form.validate_on_submit():
            venue.name = form.name.data
            venue.genres = form.genres.data
            venue.address = form.address.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.website = form.website.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data
            db.session.add(venue)
            db.session.commit()
        else:
            raise Exception('Form validation failed')
    except Exception as e:
        print('edit_venue_submission: ', e)
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    error = False
    try:
        if form.validate_on_submit():
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website=form.website.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(artist)
            db.session.commit()
            # TODO: insert form data as a new Venue record in the db, instead
            # TODO: modify data to be the data object returned from db
            # insertion
        else:
            raise Exception('Form validation failed')
    except Exception as e:
        print('create_artist_submission: ', e)
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
        # on successful db insert, flash success
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be
        # listed.')
        flash('An error occurred. Artist ' + request.form['name'] +
              ' could not be listed.')
        return render_template('forms/new_artist.html', form=form)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    shows = db.session.query(Show, Venue.name, Artist).join(Venue, Artist)
    for show, venue_name, artist in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': venue_name,
            'artist_id': show.artist_id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': str(show.start_time)
        })
        print('data: ', data[0]['start_time'])
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    error = False
    try:
        if form.validate_on_submit():
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(show)
            db.session.commit()
    except Exception as e:
        print('create_show_submission: ', e)
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
        # on successful db insert, flash success
    if error:
        # on successful db insert, flash success
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
        return render_template('forms/new_show.html', form=form)
    else:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
