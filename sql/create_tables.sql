CREATE TABLE roles(
	role_pk serial primary key,
	title varchar(32)
);

CREATE TABLE capabilities(
	capability_pk serial primary key,
	name varchar(32)
);

CREATE TABLE has(
	role_fk integer references roles (role_pk),
	capability_fk integer references capabilities (capability_pk)
);

CREATE TABLE users(
	user_id varchar(16) UNIQUE, -- all-lowercase version of username; this will function as the primary key
	username varchar(16), -- Case-sensitive username
	password varchar(64), -- 256-bit hash used, 64 characters converted to hex
	role_fk integer REFERENCES roles (role_pk)
);

CREATE TABLE assets(
	asset_pk serial primary key,
	asset_tag varchar(16),
	description text
);

CREATE TABLE facilities(
	facility_pk serial primary key,
	facility_code varchar(6),
	common_name varchar(32)
);

CREATE TABLE asset_at(
	asset_fk integer REFERENCES assets (asset_pk),
	facility_fk integer REFERENCES facilities (facility_pk),
	intake_date timestamp,
	expunge_date timestamp
);

