INSERT INTO locations (location_name)
VALUES
    ("Aberdeen"),
    ("Belfast"),
    ("Birmingham"),
    ("Bristol"),
    ("Cardiff"),
    ("Edinburgh"),
    ("Glasgow"),
    ("London"),
    ("Manchester"),
    ("Newcastle"),
    ("Norwich"),
    ("Nottingham"),
    ("Oxford"),
    ("Plymouth"),
    ("Swansea");

INSERT INTO currencies (full_name, acronym, conversion_rate)
VALUES
    ("British Pound Sterling", "GBP", 1.0),
    ("Euro", "EUR", 1.2),
    ("United States Dollar", "USD", 1.6);

SELECT @gbp_id := id FROM currencies WHERE acronym = "GBP";

INSERT INTO hotels (location_id, base_currency_id, peak_price, off_peak_price)
VALUES
    ((SELECT id FROM locations WHERE location_name = "Aberdeen"), @gbp_id, 140.0, 60.0),
    ((SELECT id FROM locations WHERE location_name = "Belfast"), @gbp_id, 130.0, 60.0),
    ((SELECT id FROM locations WHERE location_name = "Birmingham"), @gbp_id, 150.0, 70.0),
    ((SELECT id FROM locations WHERE location_name = "Bristol"), @gbp_id, 140.0, 70.0),
    ((SELECT id FROM locations WHERE location_name = "Cardiff"), @gbp_id, 120.0, 60.0),
    ((SELECT id FROM locations WHERE location_name = "Edinburgh"), @gbp_id, 160.0, 70.0),
    ((SELECT id FROM locations WHERE location_name = "Glasgow"), @gbp_id, 150.0, 70.0),
    ((SELECT id FROM locations WHERE location_name = "London"), @gbp_id, 200.0, 80.0),
    ((SELECT id FROM locations WHERE location_name = "Manchester"), @gbp_id, 180.0, 80.0),
    ((SELECT id FROM locations WHERE location_name = "Newcastle"), @gbp_id, 100.0, 60.0),
    ((SELECT id FROM locations WHERE location_name = "Norwich"), @gbp_id, 100.0, 60.0),
    ((SELECT id FROM locations WHERE location_name = "Nottingham"), @gbp_id, 120.0, 70.0),
    ((SELECT id FROM locations WHERE location_name = "Oxford"), @gbp_id, 180.0, 70.0),
    ((SELECT id FROM locations WHERE location_name = "Plymouth"), @gbp_id, 180.0, 50.0),
    ((SELECT id FROM locations WHERE location_name = "Swansea"), @gbp_id, 120.0, 50.0);

INSERT INTO room_types (type, max_occupants)
VALUES 
    ("S", 1),
    ("D", 2),
    ("F", 6);