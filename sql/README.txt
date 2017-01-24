import_data.sh - bash script which will setup an existing database for LOST and import legacy data
	takes a database name and port number for the database as arguments
create_tables.sql - psql script to create all necessary tables to track LOST personnel, facilities, and assets
import_data.py - python script to reformat lost legacy data to enable it to be assimilated into a database formatted by 'create_tables.sql'
	formatted for a specific set of OSNAP legacy data
lost_input.py - general input functions to be utilized by import_data.py
	communicates with the database without relying on a specific data set
