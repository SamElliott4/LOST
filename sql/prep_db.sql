-- vim: background=dark

-- Prep role data
INSERT INTO roles (role) VALUES ('Facilities Officer');
INSERT INTO roles (role) VALUES ('Logistics Officer');

-- Prep capability data
INSERT INTO capabilities (capability) VALUES ('Create User'); -- For future use
INSERT INTO capabilities (capability) VALUES ('Dispose Asset');
INSERT INTO capabilities (capability) VALUES ('Add Asset'); 
INSERT INTO capabilities (capability) VALUES ('Add Facility'); 
INSERT INTO capabilities (capability) VALUES ('Transfer Request');
INSERT INTO capabilities (capability) VALUES ('Approve Transfer');
INSERT INTO capabilities (capability) VALUES ('Update Transit');

-- Facility Officer capabilities
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE role='Facilities Officer'), (SELECT capability_pk FROM capabilities WHERE capability='Add Facility'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE role='Facilities Officer'), (SELECT capability_pk FROM capabilities WHERE capability='Add Asset'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE role='Facilities Officer'), (SELECT capability_pk FROM capabilities WHERE capability='Approve Transfer'));

-- Logistics Officer capabilities
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE role='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE capability='Add Facility'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE role='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE capability='Add Asset'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE role='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE capability='Dispose Asset'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE role='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE capability='Transfer Request'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE role='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE capability='Update Transit'));



