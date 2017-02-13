if [ "$#" -ne 1 ]; then
    echo "Usage: ./preflight.sh <dbname>"
    exit;
fi

	# Database prep
cd sql
bash ./import_data.sh $1 5432
cd ..

# Install the files for the LOST web service
cp -R src/* $HOME/wsgi
