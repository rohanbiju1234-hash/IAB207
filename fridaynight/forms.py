from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    IntegerField, DecimalField, DateField, TimeField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, Optional
)


class RegisterForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Surname', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    contact_number = StringField('Contact number', validators=[DataRequired(), Length(max=20)])
    street_address = StringField('Street address', validators=[DataRequired(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class EventForm(FlaskForm):
    title = StringField('Event title', validators=[DataRequired(), Length(max=150)])
    artist = StringField('Artist', validators=[Optional(), Length(max=150)])
    category = SelectField(
        'Category',
        choices=[('Jazz', 'Jazz'), ('Rock', 'Rock'), ('Hip-Hop', 'Hip-Hop'),
                 ('EDM', 'EDM'), ('R&B', 'R&B'), ('Other', 'Other')],
        validators=[DataRequired()]
    )
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Event image', validators=[
        Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'avif'], 'Images only!')
    ])

    event_date = DateField('Event date', validators=[DataRequired()])
    start_time = TimeField('Start time', validators=[DataRequired()])
    end_time = TimeField('End time', validators=[Optional()])
    venue = StringField('Venue', validators=[DataRequired(), Length(max=200)])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1)])
    ticket_price = DecimalField('General admission price ($)', validators=[DataRequired(), NumberRange(min=0)])

    # status is intentionally left out of the edit form per the brief:
    # "The owner ... should be able to update the details of the event
    # (excluding the event status)". It's only set here for the CREATE form.
    status = SelectField(
        'Status',
        choices=[('Open', 'Open'), ('Inactive', 'Inactive'),
                 ('Sold Out', 'Sold Out'), ('Cancelled', 'Cancelled')],
        validators=[DataRequired()]
    )

    acknowledgement_type = SelectField(
        'Acknowledgement of Country',
        choices=[('none', 'No Acknowledgement of Country'),
                 ('generic', 'Acknowledgement of Country: generic'),
                 ('enhanced', 'Acknowledgement of Country: enhanced')],
        validators=[DataRequired()]
    )
    traditional_custodians = StringField(
        'Traditional Custodians of this land (for the enhanced option)',
        validators=[Optional(), Length(max=200)]
    )
    acknowledgement_text = TextAreaField(
        'Your Acknowledgement of Country statement (for the enhanced option)',
        validators=[Optional()]
    )

    submit = SubmitField('Publish event')


class CommentForm(FlaskForm):
    body = TextAreaField(
        'Add a comment', validators=[DataRequired(), Length(max=1000)],
        render_kw={'rows': 2, 'placeholder': 'Ask a question or leave a comment…'}
    )
    submit = SubmitField('Post')


class BookingForm(FlaskForm):
    ticket_type = SelectField(
        'Ticket type',
        choices=[('Standard Admission', 'Standard Admission'), ('VIP', 'VIP deck seating')],
        validators=[DataRequired()]
    )
    quantity = IntegerField('Number of tickets', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Book now')


class SearchForm(FlaskForm):
    # GET form, used on the landing page - keyword + optional AI-enhanced toggle
    query = StringField('Search events, venues, artists…', validators=[Optional()])
    submit = SubmitField('Search')
