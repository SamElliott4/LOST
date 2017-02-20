Home directory for the LOST database

Contents:
	preflight.sh:
		calls create_tables.sql on an existing database passed in as the first argument
		migrates files to wsgi folder
		-usage ./preflight.sh <dbname>
