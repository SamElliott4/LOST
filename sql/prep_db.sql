-- vim: background=dark

INSERT INTO roles (title) VALUES ('Facility Officer');
INSERT INTO roles (title) VALUES ('Logistics Officer');

INSERT INTO capabilities (name) VALUES ('Create User'); -- For future use
INSERT INTO capabilities (name) VALUES ('Dispose Asset'); -- Logistics officers only for now
INSERT INTO capabilities (name) VALUES ('Add Asset'); 
INSERT INTO capabilities (name) VALUES ('Add Facility'); 
INSERT INTO capabilities (name) VALUES ('Transfer Request');
INSERT INTO capabilities (name) VALUES ('Approve Transfer');
INSERT INTO capabilities (name) VALUES ('Update Transit');

-- Facility Officer capabilities
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Facility Officer'), (SELECT capability_pk FROM capabilities WHERE name='Add Facility'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Facility Officer'), (SELECT capability_pk FROM capabilities WHERE name='Add Asset'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Facility Officer'), (SELECT capability_pk FROM capabilities WHERE name='Approve Transfer'));

-- Logistics Officer capabilities
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE name='Add Facility'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE name='Add Asset'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE name='Dispose Asset'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE name='Transfer Request'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE name='Update Transit'));



