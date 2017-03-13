This directory contains the scripts that handle import of data into a fresh LOST database. This import is not compatible with a database already in use.

Scripts:
  import_data.sh - Takes a database name and directory as args and runs import_data.py; imports data from given directory into given database
    usage: bash import_data.sh <dbname> <directory>
  import_data.py - Handles actual parsing of data files and insertion into database
    usage: Should not be called independent of import_data.sh
