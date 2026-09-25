from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)

    # relationships back to the tables that reference this user
    events = db.relationship('Event', backref='owner', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Event(db.Model):
    __tablename__ = 'events'

    # allowed values for the status column - see the assignment brief
    STATUS_OPEN = 'Open'
    STATUS_INACTIVE = 'Inactive'
    STATUS_SOLD_OUT = 'Sold Out'
    STATUS_CANCELLED = 'Cancelled'

    # allowed values for the Acknowledgement of Country selector
    ACK_NONE = 'none'
    ACK_GENERIC = 'generic'
    ACK_ENHANCED = 'enhanced'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    artist = db.Column(db.String(150))
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(200))
    venue = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    capacity = db.Column(db.Integer, nullable=False)
    ticket_price = db.Column(db.Numeric(8, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_OPEN)

    # Acknowledgement of Country fields
    acknowledgement_type = db.Column(db.String(20), nullable=False, default=ACK_NONE)
    # for the "enhanced" option, the creator fills in these to make it specific to their event
    traditional_custodians = db.Column(db.String(200))   # e.g. "the Turrbal and Yugara peoples"
    acknowledgement_text = db.Column(db.Text)             # the final statement shown on the event page

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='event', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='event', lazy=True, cascade='all, delete-orphan')

    @property
    def tickets_sold(self):
        return sum(b.quantity for b in self.bookings)

    @property
    def is_past(self):
        return self.event_date < datetime.utcnow().date()


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    order_reference = db.Column(db.String(30), unique=True, nullable=False)
    ticket_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(8, 2), nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
