from flask import Blueprint
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .models import db, User, Location, Currency, Hotel, Roomtype, Room, Booking

admin = Admin(template_mode="bootstrap3")
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(Currency, db.session))
admin.add_view(ModelView(Hotel, db.session))
admin.add_view(ModelView(Roomtype, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Booking, db.session))