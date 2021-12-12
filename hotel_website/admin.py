from flask import redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
import flask_login

from .models import db, User, Location, Currency, Roomtype, Room, Booking


class CustomIndexView(AdminIndexView):
    @expose("/")
    def custom_index(self):
        if self.is_accessible():
            return self.render(self._template)
        else:
            return self.inaccessible_callback()

    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


class CustomModelView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


admin = Admin(template_mode="bootstrap3", index_view=CustomIndexView())

admin.add_view(CustomModelView(User, db.session))
admin.add_view(CustomModelView(Location, db.session))
admin.add_view(CustomModelView(Currency, db.session))
admin.add_view(CustomModelView(Roomtype, db.session))
admin.add_view(CustomModelView(Room, db.session))
admin.add_view(CustomModelView(Booking, db.session))
