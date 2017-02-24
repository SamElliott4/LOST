if [ "$#" -ne 1 ]; then
    echo "Usage: ./preflight.sh <dbname>"
    exit;
fi

	# Database prep
cd sql

# build tables
psql $1 < create_tables.sql

# insert core information into new db (e.g. existing roles and the capabilities of those roles)
psql $1 < prep_db.sql
cd ..

# Install the files for the LOST web service
cp -R src/* $HOME/wsgi
