INSERT INTO location (name)
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

INSERT INTO currency (full_name, acronym, conversion_rate)
VALUES
    ("British Pound Sterling", "GBP", 1.0),
    ("Euro", "EUR", 1.2),
    ("United States Dollar", "USD", 1.6);

SELECT @gbp_id := id FROM currency WHERE acronym = "GBP";

INSERT INTO hotel (location_id, currency_id, peak_price, off_peak_price, image)
VALUES
    ((SELECT id FROM location WHERE name = "Aberdeen"), @gbp_id, 140.0, 60.0, "images/aberdeen.jpg"),
    ((SELECT id FROM location WHERE name = "Belfast"), @gbp_id, 130.0, 60.0, "images/belfast.jpg"),
    ((SELECT id FROM location WHERE name = "Birmingham"), @gbp_id, 150.0, 70.0, "images/birmingham.jpg"),
    ((SELECT id FROM location WHERE name = "Bristol"), @gbp_id, 140.0, 70.0, "images/bristol.jpg"),
    ((SELECT id FROM location WHERE name = "Cardiff"), @gbp_id, 120.0, 60.0, "images/cardiff.jpg"),
    ((SELECT id FROM location WHERE name = "Edinburgh"), @gbp_id, 160.0, 70.0, "images/edinburgh.jpg"),
    ((SELECT id FROM location WHERE name = "Glasgow"), @gbp_id, 150.0, 70.0, "images/glasgow.jpg"),
    ((SELECT id FROM location WHERE name = "London"), @gbp_id, 200.0, 80.0, "images/london.jpg"),
    ((SELECT id FROM location WHERE name = "Manchester"), @gbp_id, 180.0, 80.0, "images/manchester.jpg"),
    ((SELECT id FROM location WHERE name = "Newcastle"), @gbp_id, 100.0, 60.0, "images/newcastle.jpg"),
    ((SELECT id FROM location WHERE name = "Norwich"), @gbp_id, 100.0, 60.0, "images/norwich.jpg"),
    ((SELECT id FROM location WHERE name = "Nottingham"), @gbp_id, 120.0, 70.0, "images/nottingham.jpg"),
    ((SELECT id FROM location WHERE name = "Oxford"), @gbp_id, 180.0, 70.0, "images/oxford.jpg"),
    ((SELECT id FROM location WHERE name = "Plymouth"), @gbp_id, 180.0, 50.0, "images/plymouth.jpg"),
    ((SELECT id FROM location WHERE name = "Swansea"), @gbp_id, 120.0, 50.0, "images/swansea.jpg");

INSERT INTO roomtype (room_type, max_occupants)
VALUES 
    ("S", 1),
    ("D", 2),
    ("F", 6);