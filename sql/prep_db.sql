INSERT INTO roles (title) VALUES ('Facility Officer');
INSERT INTO roles (title) VALUES ('Logistics Officer');

INSERT INTO capabilities (name) VALUES ('create user'); -- For future use
INSERT INTO capabilities (name) VALUES ('dispose asset'); -- Logistics officers only for now
INSERT INTO capabilities (name) VALUES ('add asset'); -- Both vlogistics and facility officers

-- Facility Officer capabilities
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Facility Officer'), (SELECT capability_pk FROM capabilities WHERE name='add asset'));

-- Logistics Officer capabilities
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE name='add asset'));
INSERT INTO has (role_fk, capability_fk) VALUES ((SELECT role_pk FROM roles WHERE title='Logistics Officer'), (SELECT capability_pk FROM capabilities WHERE name='dispose asset'));
