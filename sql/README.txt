This directory contains all scripts and supporting dosuments needed to set up the LOST database

Contents:
	create_tables.sql - Create all necessary tables for the database (incomplete)
	  -usage: psql <dbname> < create_tables.sql

	prep_db.sql - Adds baseline information that the database needs to support the web application
	  -usage: psql <dbname> < prep_db.sql
