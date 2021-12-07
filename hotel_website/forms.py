from datetime import date, timedelta

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FormField, RadioField, ValidationError
from wtforms_components import DateField, IntegerField, DateRange, EmailField
from wtforms.validators import InputRequired, Length, NumberRange, Regexp

from .constants import COUNTRIES_TUPLES, CARD_TYPES_TUPLES


class UsernamePasswordForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])


class WhereToForm(FlaskForm):
    location = SelectField("Location", coerce=int, validators=[InputRequired()])
    booking_start = DateField("Booking start", validators=[InputRequired()])
    booking_end = DateField("Booking end", format="%Y-%m-%d", validators=[InputRequired()])
    guests = IntegerField(
        "Number of guests", render_kw={"placeholder": "Number of guests"},
        validators=[InputRequired(), NumberRange(min=1, max=6)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add validators and defaults on form creation so dates are correct
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # TODO: Missed requirement that bookings are not made more than 3 months in advance!
        # Implement this restriction everywhere.
        # By 3 months, they seem to mean 90 days exactly, since that's what in the table

        self.booking_start.validators += [DateRange(min=today)]
        self.booking_end.validators += [DateRange(min=tomorrow)]

        if not self.booking_start.data:
            self.booking_start.data = today
        if not self.booking_end.data:
            self.booking_end.data = tomorrow


class AddressForm(FlaskForm):
    # TODO: Probably need to add more placeholder text and styling, but I'm bored now, do it later
    address_1 = StringField(
        "Address Line 1",
        render_kw={"placeholder": "Address Line 1"},
        validators=[InputRequired()])
    address_2 = StringField("Address Line 2", render_kw={"placeholder": "Address Line 2"})
    # Longest postcodes globally seem to be ~12 chars
    postcode = StringField(
        "Postcode",
        render_kw={"placeholder": "Postcode"},
        validators=[InputRequired(), Length(min=1, max=15)])
    country = SelectField("Country", choices=COUNTRIES_TUPLES, validators=[InputRequired()])


class CardExpiryForm(FlaskForm):
    expiry_month = IntegerField("Month", validators=[InputRequired(), NumberRange(min=1, max=12)])
    expiry_year = IntegerField("Year", validators=[InputRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()

        self.expiry_year.validators += [NumberRange(min=today.year, max=today.year + 15)]


class CardForm(FlaskForm):
    card_type = SelectField("Card Type", choices=CARD_TYPES_TUPLES, validators=[InputRequired()])
    card_number = StringField("Card Number", render_kw={"placeholder": "Card Number"}, validators=[InputRequired()])
    # Regex: exactly three digits
    security_code = StringField(
        "Security Code", render_kw={"placeholder": "Security Code"},
        validators=[InputRequired(), Regexp(r"^\d{3}$")])
    expiry_date = FormField(CardExpiryForm, label="Expiry Date")

    def validate_card_number(form, field):
        # Only spaces and numbers are legal for the field
        try:
            spaces_stripped = "".join(field.data.split())
            int(spaces_stripped)
        except ValueError:
            raise ValidationError


class BookingForm(FlaskForm):
    full_name = StringField("Full Name", render_kw={"placeholder": "Full Name"}, validators=[InputRequired()])
    email = EmailField("Email", render_kw={"placeholder": "Email"}, validators=[InputRequired()])

    address = FormField(AddressForm, label="Address")

    card_details = FormField(CardForm, label="Card Details")
