This direcetory contains scripts to export all necessary data from an existing LOST database in such a form that it can be migrated into another database.

Scripts:
  export_data.sh - Takes a database name and directory as arguments
    usage: bash export_data.sh <dbname> <directory>
           Will clear contents of directory passed, or create it if one does not exist

  export_data.py - Script to handle the actual data export
    usage: called by export_data.sh; should not be run independently
