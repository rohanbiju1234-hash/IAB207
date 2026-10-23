import os
import random
import string
import uuid
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename


from . import db
from .models import User, Event, Booking, Comment
from .forms import RegisterForm, LoginForm, EventForm, CommentForm, BookingForm, SearchForm, CancelEventForm
from .ai_search import rank_events_by_query   # AI-enhanced discovery - see ai_search.py

main = Blueprint('main', __name__)


# ---------- helpers ----------

def generate_order_reference():
    stamp = datetime.utcnow().strftime('%Y%m%d')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f'FN-{stamp}-{suffix}'


def refresh_event_status(event):
    """Auto-flip an Open event to Inactive once its date has passed.
    Sold Out / Cancelled are left as-is since those are explicit states."""
    if event.status == Event.STATUS_OPEN and event.is_past:
        event.status = Event.STATUS_INACTIVE
        db.session.commit()


CUSTODIANS = {
'brisbane': 'the Turrbal and Jagera (Yuggera) peoples',
'sydney': 'the Gadigal people of the Eora Nation',
'melbourne': 'the Wurundjeri Woi-wurrung and Bunurong peoples of the Kulin Nation',
'canberra': 'the Ngunnawal people',
'adelaide': 'the Kaurna people',
'perth': 'the Whadjuk people of the Noongar Nation',
'hobart': 'the muwinina people',
'darwin': 'the Larrakia people',
        }

def get_custodians(form):
    if form.ack_location.data == 'other':
        return form.traditional_custodians.data
    return CUSTODIANS.get(form.ack_location.data)


def build_acknowledgement(form):
    if form.acknowledgement_type.data == 'generic':
        return('We acknowledge the Traditional Custodians of the land on which this event '
              'takes place, and pay our respects to their Elders past and present.'  )



    if form.acknowledgement_type.data == 'enhanced':
        statement = f'We acknowledge {get_custodians(form)}, the Traditional Custodians of the Land'
        if form.ack_place.data:
            statement += f' where we gather - {form.ack_place.data}'
        statement += ('. We pay our respects to their Elders past and present, '
                     'and recognise their continuing connection to Country.')
        if form.ack_reflection.data:
            statement += ' ' + form.ack_reflection.data
        return statement
    return None
 






# ---------- landing page / browse + search ----------

@main.route('/')
def index():
    search_form = SearchForm()
    query = request.args.get('query', '').strip()
    category = request.args.get('category', 'all')

    events = Event.query.order_by(Event.event_date.asc()).all()
    for e in events:
        refresh_event_status(e)

    if category and category != 'all':
        events = [e for e in events if e.category.lower() == category.lower()]

    if query:
        # AI-enhanced discovery: ranks by semantic similarity instead of
        # exact substring matching alone. See ai_search.py for the approach
        # and how to swap in sentence-transformers embeddings.
        events = rank_events_by_query(events, query)

    categories = ['All', 'Jazz', 'Rock', 'Hip-Hop', 'EDM', 'R&B']
    return render_template(
        'index.html', events=events, search_form=search_form,
        query=query, active_category=category, categories=categories
    )


# ---------- event details, comments, booking ----------

@main.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    refresh_event_status(event)

    comment_form = CommentForm()
    booking_form = BookingForm()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please log in to do that.', 'warning')
            return redirect(url_for('main.login'))

        if request.form.get('form_name') == 'comment' and comment_form.validate_on_submit():
            comment = Comment(body=comment_form.body.data, author=current_user, event=event)
            db.session.add(comment)
            db.session.commit()
            flash('Comment posted.', 'success')
            return redirect(url_for('main.event_details', event_id=event.id))

        if request.form.get('form_name') == 'booking' and booking_form.validate_on_submit():
            if event.status != Event.STATUS_OPEN:
                flash('This event is not currently open for booking.', 'danger')
                return redirect(url_for('main.event_details', event_id=event.id))

            unit_price = float(event.ticket_price) if booking_form.ticket_type.data == 'Standard Admission' else float(event.ticket_price) + 25
            quantity = booking_form.quantity.data
            booking = Booking(
                order_reference=generate_order_reference(),
                ticket_type=booking_form.ticket_type.data,
                quantity=quantity,
                total_price=unit_price * quantity,
                user=current_user,
                event=event,
            )
            db.session.add(booking)

            # naive sold-out check based on capacity
            if event.tickets_sold + quantity >= event.capacity:
                event.status = Event.STATUS_SOLD_OUT

            db.session.commit()
            flash(f'Booking confirmed! Your order reference is {booking.order_reference}.', 'success')
            return redirect(url_for('main.event_details', event_id=event.id))

    comments = Comment.query.filter_by(event_id=event.id).order_by(Comment.created_at.desc()).all()
    return render_template(
        'event_details.html', event=event, comment_form=comment_form,
        booking_form=booking_form, comments=comments
    )


# ---------- create / edit / cancel event ----------

@main.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        image_filename = save_event_image(form.image.data)

        event = Event(
            title=form.title.data,
            artist=form.artist.data,
            category=form.category.data,
            description=form.description.data,
            image_filename=image_filename,
            venue=form.venue.data,
            event_date=form.event_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            capacity=form.capacity.data,
            ticket_price=form.ticket_price.data,
            status=Event.STATUS_OPEN,
            acknowledgement_type=form.acknowledgement_type.data,
            traditional_custodians=get_custodians(form),
            acknowledgement_text=build_acknowledgement(form),
            owner=current_user,
        )
        db.session.add(event)
        db.session.commit()
        flash('Event published!', 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('create_event.html', form=form, editing=False)


@main.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.owner_id != current_user.id:
        abort(403)



    form = EventForm(obj=event)
    if request.method == 'GET':
        form.status.data = event.status 

        for key, name in CUSTODIANS.items():
            if name == event.traditional_custodians:
                form.ack_location.data = key

     # shown but disabled - see template note

    if form.validate_on_submit():
        event.title = form.title.data
        event.artist = form.artist.data
        event.category = form.category.data
        event.description = form.description.data
        event.venue = form.venue.data
        event.event_date = form.event_date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.capacity = form.capacity.data
        event.ticket_price = form.ticket_price.data
        event.acknowledgement_type = form.acknowledgement_type.data
        event.traditional_custodians = get_custodians(form)
        event.acknowledgement_text = build_acknowledgement(form)
        # NOTE: event.status is deliberately NOT updated here - the brief
        # says owners can edit everything except the status.

        new_image = save_event_image(form.image.data)
        if new_image:
            event.image_filename = new_image

        db.session.commit()
        flash('Event updated.', 'success')
        return redirect(url_for('main.event_details', event_id=event.id))

    return render_template('create_event.html', form=form, editing=True, event=event)


@main.route('/event/<int:event_id>/cancel', methods=['GET', 'POST'])
@login_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.owner_id != current_user.id:
        abort(403)



    form = CancelEventForm()
    if form.validate_on_submit():
        event.status = Event.STATUS_CANCELLED
        db.session.commit()
        flash('Event cancelled.', 'info')
        return redirect(url_for('main.event_details', event_id=event.id))
    

    return render_template('cancel_event.html', event=event, form=form)



   


@main.route('/my-events')
@login_required
def my_events():
    events = Event.query.filter_by(owner_id=current_user.id).order_by(Event.event_date.desc()).all()
    return render_template('my_events.html', events=events)


def save_event_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    from flask import current_app
    filename = secure_filename(file_storage.filename)
    unique_name = f'{uuid.uuid4().hex[:8]}_{filename}'
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file_storage.save(path)
    return filename


# ---------- booking history ----------

@main.route('/bookings')
@login_required
def booking_history():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booked_at.desc()).all()
    return render_template('booking_history.html', bookings=bookings)


# ---------- auth ----------

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('An account with that email already exists.', 'danger')
            return render_template('register.html', form=form)

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data.lower(),
            contact_number=form.contact_number.data,
            street_address=form.street_address.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Incorrect email or password.', 'danger')

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ---------- Acknowledgement of Country info page ----------

@main.route('/acknowledgement-of-country')
def acknowledgement_info():
    return render_template('acknowledgement_info.html')
