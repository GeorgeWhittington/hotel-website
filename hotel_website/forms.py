# George Whittington, Student ID: 20026036, 2022

from datetime import date, timedelta

from flask import flash
from flask_wtf import Form, FlaskForm
from wtforms import Field, PasswordField, SelectField, FormField, ValidationError, MonthField, SelectMultipleField
from wtforms_components import DateField, IntegerField, DateRange, EmailField, StringField
from wtforms.validators import InputRequired, Length, NumberRange, Regexp

from .constants import COUNTRIES_TUPLES, CARD_TYPES_TUPLES, MAX_GUESTS, LOCATION_ERR, DURATION_ERR, GUESTS_ERR


class UsernamePasswordForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])


class UsernamePasswordUpdateForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Change Password")


class WhereToForm(FlaskForm):
    location = SelectField("Location", coerce=int, validators=[InputRequired()])
    booking_start = DateField(
        "Booking start", render_kw={"title": "Enter booking start date"},
        format="%Y-%m-%d", validators=[InputRequired()])
    booking_end = DateField(
        "Booking end", render_kw={"title": "Enter booking end date"},
        format="%Y-%m-%d", validators=[InputRequired()])
    guests = IntegerField(
        "Number of guests", render_kw={"placeholder": "Number of guests"},
        validators=[InputRequired(), NumberRange(min=1, max=MAX_GUESTS)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add validators and defaults on form creation so dates are correct
        today = date.today()
        tomorrow = today + timedelta(days=1)
        three_months = today + timedelta(days=90)

        self.booking_start.validators += [DateRange(min=today, max=three_months)]
        self.booking_end.validators += [DateRange(min=tomorrow, max=three_months)]

    def check(self):
        """Checks the form response for errors.
        If any are found, an appropriate error message is flashed and None is returned.
        If the response is fine, a dictionary is returned which can be used to fill url args with.
        """
        duration_err = False
        if self.validate_on_submit():
            if not self.test_duration(self.booking_start.data, self.booking_end.data):
                return {
                    "location": self.location.data,
                    "booking_start": self.booking_start.data,
                    "booking_end": self.booking_end.data,
                    "guests": self.guests.data
                }
            else:
                duration_err = True

        if self.location.errors:
            flash(LOCATION_ERR)

        if duration_err or self.booking_start.errors or self.booking_end.errors:
            flash(DURATION_ERR)

        if self.guests.errors:
            flash(GUESTS_ERR)

    @staticmethod
    def test_duration(booking_start: date, booking_end: date) -> bool:
        """If the booking duration is invalid, returns True"""
        today = date.today()
        three_months = today + timedelta(days=90)

        return (
            booking_start is None or
            booking_end is None or
            booking_start < today or
            booking_end <= today or
            booking_end > three_months or
            booking_start >= booking_end
        )

    @staticmethod
    def test_guests(guests: int) -> bool:
        """If the number of guests is invalid, returns True"""
        return (guests is None or
                guests < 1 or
                guests > MAX_GUESTS)


class AddressForm(Form):
    """Form for entering address.

    This form is only to be used nested inside a parent form which has csrf enabled.
    Used on its own it is *not* secure.
    """
    class Meta:
        csrf = False

    address_1 = StringField(
        "Address Line 1",
        render_kw={"placeholder": "Address Line 1"},
        validators=[InputRequired()])
    address_2 = StringField("Address Line 2", render_kw={"placeholder": "Address Line 2"})
    # Longest postcodes globally seem to be ~12 chars
    postcode = StringField(
        "Postcode",
        render_kw={"placeholder": "Postcode", "minlength": "1", "maxlength": "15"},
        validators=[InputRequired(), Length(min=1, max=15)])
    country = SelectField("Country", choices=COUNTRIES_TUPLES, validators=[InputRequired()])


class CardExpiryForm(Form):
    """Form for entering card expiry.

    This form is only to be used nested inside a parent form which has csrf enabled.
    Used on its own it is *not* secure.
    """
    class Meta:
        csrf = False

    expiry_month = IntegerField(
        "Month",
        render_kw={"placeholder": "Month"},
        validators=[InputRequired(), NumberRange(min=1, max=12)])
    expiry_year = IntegerField(
        "Year",
        render_kw={"placeholder": "Year"},
        validators=[InputRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()

        self.expiry_year.validators += [NumberRange(min=today.year, max=today.year + 15)]


class CardForm(Form):
    """Form for entering card details.

    This form is only to be used nested inside a parent form which has csrf enabled.
    Used on its own it is *not* secure.
    """
    class Meta:
        csrf = False

    card_type = SelectField("Card Type", choices=CARD_TYPES_TUPLES, validators=[InputRequired()])
    card_number = StringField(
        "Card Number", render_kw={"placeholder": "Card Number"},
        validators=[InputRequired(), Length(max=25)])
    # Regex: exactly three digits
    security_code = StringField(
        "Security Code", render_kw={"placeholder": "Security Code"},
        validators=[InputRequired(), Regexp(r"^\d{3,4}$")])
    expiry_date = FormField(CardExpiryForm, label="Expiry Date")

    def validate_card_number(self, field: Field) -> None:
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


class MonthAndLocationForm(FlaskForm):
    month = MonthField("Month", validators=[InputRequired()])
    location = SelectField("Hotel Location", coerce=int, validators=[InputRequired()])


class MonthAndLocationsForm(FlaskForm):
    month = MonthField("Month", validators=[InputRequired()])
    locations = SelectMultipleField("Hotel Locations", coerce=int, render_kw={"aria-describedby": "locationHelp"}, validators=[InputRequired()])
