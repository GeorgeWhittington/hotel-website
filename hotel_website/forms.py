from datetime import date, timedelta

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField
from wtforms_components import DateField, IntegerField, DateRange
from wtforms.validators import InputRequired, Length, NumberRange


class UsernamePasswordForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])


class WhereToForm(FlaskForm):
    location = SelectField("Location", coerce=int, validators=[InputRequired()])
    # write a custom validator for these? need something that'll stick a clientside min on atleast
    booking_start = DateField("Booking start", validators=[InputRequired()])
    booking_end = DateField("Booking end", format="%Y-%m-%d", validators=[InputRequired()])
    guests = IntegerField("Number of guests", render_kw={"placeholder": "Number of guests"}, validators=[InputRequired(), NumberRange(min=1)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add validators and defaults on form creation so dates are correct
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        self.booking_start.validators += [DateRange(min=today)]
        self.booking_end.validators += [DateRange(min=tomorrow)]

        if not self.booking_start.data:
            self.booking_start.data = today
        if not self.booking_end.data:
            self.booking_end.data = tomorrow