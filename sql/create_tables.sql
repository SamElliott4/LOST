CREATE TABLE users(
	user_id varchar(16) UNIQUE, -- all-lowercase version of username; this will function as the primary key
	username varchar(16), -- Case-sensitive username
	password varchar(64) -- 256-bit hash used, 64 characters converted to hex
);
