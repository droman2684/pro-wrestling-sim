INSERT INTO private_passenger_type
(private_passenger_type)
VALUES
('Personal Use or Farm Use - Nonfleet Vehicle'),
('Business Use - Nonfleet Vehicle'),
('Personal Use or Business Use - Fleet Vehicle'),
('Farm Use - Fleet Vehicle');

CREATE TABLE private_passenger_operator_experience
(ID INTEGER PRIMARY KEY,
private_passenger_operator_experience TEXT);

CREATE TABLE private_passenger_use
(ID INTEGER PRIMARY KEY,
private_passenger_use TEXT);

CREATE TABLE ppt_class_code
(ID INTEGER PRIMARY KEY,
private_passenger_type TEXT,
private_passenger_operator_experience TEXT,
private_passenger_use TEXT,
ppt_class_code INTEGER);

CREATE TABLE ppt_al_fleet_size_factor
(ID INTEGER PRIMARY KEY,
state_code TEXT,
effective_date DATE,
min_fleet_size INTEGER,
max_fleet_size INTEGER,
ppt_al_fleet_size_factor);


CREATE TABLE ppt_al_age_factor (
ID	INTEGER PRIMARY KEY,
state_code	TEXT,
effective_date	DATE,
ppt_vehicle_age	INTEGER,
ppt_al_age_factor	REAL(10, 3));

CREATE TABLE ppt_al_ocn_factor
(ID INTEGER PRIMARY KEY,
effective_date DATE,
state_code TEXT,
min_ocn INTEGER,
max_ocn INTEGER,
ppt_al_ocn_factor REAL (10,3));

CREATE TABLE ppt_al_naics_factor
(ID INTEGER PRIMARY KEY,
effective_date DATE,
state_code TEXT,
naics_code INTEGER,
ppt_al_naics_factor REAL (10,3));

CREATE TABLE ppt_al_ilf_factor
(ID INTEGER PRIMARY KEY,
effective_date DATE,
state_code TEXT,
liability_limit_csl TEXT,
ppt_al_ilf_factor REAL (10,3));

CREATE TABLE ppt_al_deductible_factor
(ID INTEGER PRIMARY KEY,
effective_date DATE,
state_code TEXT,
liability_deductible TEXT,
ppt_al_deductible_factor);