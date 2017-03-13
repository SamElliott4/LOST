-- vim: background=dark

CREATE TABLE roles(
	role_pk serial primary key,
	role varchar(32) --Name of the role, e.g. 'Facility Officer'
);

CREATE TABLE capabilities(
	capability_pk serial primary key,
	capability varchar(32) -- Name of the function, e.g. 'Add Asset' or 'Dispose Asset'
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
	role_fk integer REFERENCES roles (role_pk),
	active boolean  -- Reflects wether or not a user is allowed to log in
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
	intake_dt timestamp, -- time of arrival of asset to associated facility
	expunge_dt timestamp -- time of assets removal from associated facility
);

-- requests for asset transfer; only contains data about the request, not about the transfer itself
CREATE TABLE transfer_requests(
	request_id varchar(16) UNIQUE, -- used to join transfer_request and asset_moving tables
	requester varchar(16) references users(user_id), -- Logistics officer that requested the transfer
	request_dt timestamp, -- time of request
	src integer references facilities(facility_pk), -- where the asset is currently located
	dest integer references facilities(facility_pk), -- where the asset would be transfered to
	asset_fk integer references assets(asset_pk), -- the asset to be moved
	approver varchar(16) references users(user_id), -- Facilities Officer that approved (or rejected) the request
	approve_dt timestamp, -- time of approval/rejection
	status integer -- 0: pending, 1: approved, -1: rejected
);

CREATE TABLE asset_moving(
	request_id varchar(16) references transfer_requests(request_id),
	asset_fk integer references assets(asset_pk), -- asset being transfered
	src integer references facilities(facility_pk), -- where from
	dest integer references facilities(facility_pk), -- where to
	load_dt timestamp, -- when the asset left src facility
	unload_dt timestamp -- when the asset reached dest facility
);
