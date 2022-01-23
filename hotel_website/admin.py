from calendar import monthrange
from datetime import date

from flask import redirect, url_for, request, flash
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
import flask_login
from sqlalchemy import text
from sqlalchemy.sql import func
from wtforms import StringField, SelectField

from .constants import ROOM_TYPES, COUNTRIES_TUPLES, CARD_TYPES_TUPLES
from .forms import MonthAndLocationForm, MonthAndLocationsForm
from .models import db, User, Location, Currency, Roomtype, Room, Booking


class CustomIndexView(AdminIndexView):
    """Custom admin site index view, to make it fully inaccessible to non-admin users."""
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
    """Custom admin site model view, to make it fully inaccessible to non-admin users."""
    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


class BookingAnalyticsViews(BaseView):
    @expose("/")
    def index(self):
        return self.render("/admin/analytics_home.html")

    @expose("/monthly_bookings", methods=["GET", "POST"])
    def monthly_bookings(self):
        form = MonthAndLocationForm()

        locations = Location.query.with_entities(Location.id, Location.name).order_by(Location.name).all()
        form.location.choices = [(loc_id, loc_name) for loc_id, loc_name in locations]

        if request.method == "POST":
            if form.validate_on_submit():
                month_start = form.month.data
                month_end = date(
                    year=month_start.year,
                    month=month_start.month,
                    day=monthrange(month_start.year, month_start.month)[1])

                bookings = Location.query.with_entities(Booking).join(Location.rooms, Room.bookings).where(
                    Location.id == form.location.data,
                    # Logic for testing if there is any overlap of ranges from:
                    # https://stackoverflow.com/a/3269471
                    month_start <= Booking.booking_end,
                    Booking.booking_start <= month_end).all()

                return self.render(
                    "/admin/monthly_bookings.html", form=form,
                    bookings=bookings, room_types=ROOM_TYPES)

            flash("Please enter a location.")

        return self.render("/admin/monthly_bookings.html", form=form)

    @expose("/compare_bookings", methods=["GET", "POST"])
    def compare_bookings(self):
        form = MonthAndLocationsForm()

        locations = Location.query.with_entities(Location.id, Location.name).order_by(Location.name).all()
        form.locations.choices = [(loc_id, loc_name) for loc_id, loc_name in locations]

        if form.validate_on_submit():
            month_start = form.month.data
            month_end = date(
                year=month_start.year,
                month=month_start.month,
                day=monthrange(month_start.year, month_start.month)[1])

            # A subquery is created for a total count and also each
            # room type's count, then joined onto the main query.
            room_types = Roomtype.query.order_by(Roomtype.max_occupants).all()
            subquery_labels = [("total_count", None)]
            subquery_labels += [(f"{ROOM_TYPES[rt.room_type]}_count", rt.room_type) for rt in room_types]
            labels = (text(label) for label, _ in subquery_labels)

            subquerys = []
            for label, room_type in subquery_labels:
                subquery = Booking.query.with_entities(
                    Room.location_id,
                    func.count(Booking.id).label(label))
                subquery = subquery.join(Booking.room).where(
                    # Logic for testing if there is any overlap of ranges from:
                    # https://stackoverflow.com/a/3269471
                    month_start <= Booking.booking_end,
                    Booking.booking_start <= month_end
                )

                if room_type:
                    subquery = subquery.join(Room.room_type).where(
                        Roomtype.room_type == room_type)

                subquery = subquery.group_by(Room.location_id).subquery()
                subquerys.append(subquery)

            bookings = Location.query.with_entities(Location, *labels)
            for subquery in subquerys:
                bookings = bookings.outerjoin(subquery, Location.id == subquery.c.location_id)
            bookings = bookings.where(Location.id.in_(form.locations.data)).all()

            return self.render(
                "/admin/compare_bookings.html", form=form, bookings=bookings,
                month=month_start.strftime("%B %Y"), room_types=room_types,
                ROOM_TYPES=ROOM_TYPES)

        return self.render("/admin/compare_bookings.html", form=form)

    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


class UserView(CustomModelView):
    column_exclude_list = ["password"]
    form_excluded_columns = ["bookings"]
    form_widget_args = {
        'password': {
            'disabled': True
        }
    }
    form_extra_fields = {
        "raw_password": StringField()
    }

    def create_model(self, form):
        """User creation from form input is overridden to correctly handle hashed passwords."""
        try:
            model = User.create_user(
                username=form.username.data,
                raw_password=form.raw_password.data,
                admin=form.admin.data)
            self.session.add(model)
            self._on_model_change(form, model, True)
            self.session.commit()
        except Exception:
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, True)

        return model

    def update_model(self, form, model):
        """User object updates from form input are overridden to correctly handle hashed passwords."""
        try:
            if form.username.data:
                model.username = form.username.data

            if form.admin.data:
                model.admin = form.admin.data

            if form.raw_password.data:
                model.update_password(form.raw_password.data)

            self._on_model_change(form, model, False)
            self.session.commit()
        except Exception:
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, False)

        return True


class CurrencyView(CustomModelView):
    form_excluded_columns = ["hotels"]


class RoomtypeView(CustomModelView):
    form_excluded_columns = ["rooms"]


class RoomView(CustomModelView):
    form_excluded_columns = ["bookings"]


class BookingView(CustomModelView):
    can_export = True
    form_excluded_columns = ["date_created", "date_updated"]

    form_choices = {
        "country": COUNTRIES_TUPLES,
        "card_type": CARD_TYPES_TUPLES
    }


admin = Admin(template_mode="bootstrap4", index_view=CustomIndexView())

admin.add_view(UserView(User, db.session))
admin.add_view(CustomModelView(Location, db.session))
admin.add_view(CurrencyView(Currency, db.session))
admin.add_view(RoomtypeView(Roomtype, db.session))
admin.add_view(RoomView(Room, db.session))
admin.add_view(BookingView(Booking, db.session))

admin.add_view(BookingAnalyticsViews(name='Booking Analytics', endpoint='analytics'))
