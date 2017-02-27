-- vim: background=dark

CREATE TABLE roles(
	role_pk serial primary key,
	title varchar(32) --Name of the role, e.g. 'Facility Officer'
);

CREATE TABLE capabilities(
	capability_pk serial primary key,
	name varchar(32) -- Name of the function, e.g. 'add asset' or 'dispose asset'
);

-- joins roles and capabilities tables
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
	asset_tag varchar(16) UNIQUE, -- unique identifying tag for the asset
	description text,
	status integer -- 1 for active 0 for inactive; an asset that has not been disposed is active until disposal, regardless of location
);

CREATE TABLE facilities(
	facility_pk serial primary key,
	f_code varchar(6) UNIQUE, -- shorthand code to refer to the facility, e.g. 'HQ'
	common_name varchar(32) UNIQUE -- common name of the facility, e.g. 'Headquarters'
);

-- joins assets with facilities
-- tracks date range asset was located at a given facility
CREATE TABLE asset_at(
	asset_fk integer REFERENCES assets (asset_pk),
	facility_fk integer REFERENCES facilities (facility_pk),
	intake_date timestamp, -- time of arrival of asset to associated facility
	expunge_date timestamp -- time of assets removal from associated facility
);

