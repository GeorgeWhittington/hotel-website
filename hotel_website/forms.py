from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class UsernamePasswordForm(FlaskForm):
    username = StringField("username", validators=[DataRequired(), Length(max=20)])
    password = PasswordField("password", validators=[DataRequired()])
