
psql $1 -f create_tables.sql

curl https://classes.cs.uoregon.edu//17W/cis322/files/osnap_legacy.tar.gz | tar xvz

python3 import_data.py $1 $2


