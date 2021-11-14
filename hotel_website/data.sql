INSERT INTO currency (full_name, acronym, conversion_rate)
VALUES
    ("British Pound Sterling", "GBP", 1.0),
    ("Euro", "EUR", 1.2),
    ("United States Dollar", "USD", 1.6);

SELECT @gbp_id := id FROM currency WHERE acronym = "GBP";

INSERT INTO location (name, currency_id, peak_price, off_peak_price, image)
VALUES
    ("Aberdeen", @gbp_id, 140.0, 60.0, "images/aberdeen.jpg"),
    ("Belfast", @gbp_id, 130.0, 60.0, "images/belfast.jpg"),
    ("Birmingham", @gbp_id, 150.0, 70.0, "images/birmingham.jpg"),
    ("Bristol", @gbp_id, 140.0, 70.0, "images/bristol.jpg"),
    ("Cardiff", @gbp_id, 120.0, 60.0, "images/cardiff.jpg"),
    ("Edinburgh", @gbp_id, 160.0, 70.0, "images/edinburgh.jpg"),
    ("Glasgow", @gbp_id, 150.0, 70.0, "images/glasgow.jpg"),
    ("London", @gbp_id, 200.0, 80.0, "images/london.jpg"),
    ("Manchester", @gbp_id, 180.0, 80.0, "images/manchester.jpg"),
    ("Newcastle", @gbp_id, 100.0, 60.0, "images/newcastle.jpg"),
    ("Norwich", @gbp_id, 100.0, 60.0, "images/norwich.jpg"),
    ("Nottingham", @gbp_id, 120.0, 70.0, "images/nottingham.jpg"),
    ("Oxford", @gbp_id, 180.0, 70.0, "images/oxford.jpg"),
    ("Plymouth", @gbp_id, 180.0, 50.0, "images/plymouth.jpg"),
    ("Swansea", @gbp_id, 120.0, 50.0, "images/swansea.jpg");

INSERT INTO roomtype (room_type, max_occupants)
VALUES 
    ("S", 1),
    ("D", 2),
    ("F", 6);