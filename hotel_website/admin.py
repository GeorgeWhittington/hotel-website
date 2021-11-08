from flask import redirect, url_for, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import flask_login

from .models import db, User, Location, Currency, Hotel, Roomtype, Room, Booking

admin = Admin(template_mode="bootstrap3")


class CustomModelView(ModelView):
    def is_accessible(self):
        print(f"{flask_login.current_user.is_authenticated} {type(flask_login.current_user)}")
        return flask_login.current_user.is_authenticated and flask_login.current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


admin.add_view(CustomModelView(User, db.session))
admin.add_view(CustomModelView(Location, db.session))
admin.add_view(CustomModelView(Currency, db.session))
admin.add_view(CustomModelView(Hotel, db.session))
admin.add_view(CustomModelView(Roomtype, db.session))
admin.add_view(CustomModelView(Room, db.session))
admin.add_view(CustomModelView(Booking, db.session))