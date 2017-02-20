if [ "$#" -ne 1 ]; then
    echo "Usage: ./preflight.sh <dbname>"
    exit;
fi

	# Database prep
cd sql
psql $1 < create_tables.sql
cd ..

# Install the files for the LOST web service
cp -R src/* $HOME/wsgi
