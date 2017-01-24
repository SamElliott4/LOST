Scripts supporting the LOST database are stored here. 

Only import_data.sh should be run under normal circumstances.

Scripts:		Usage
import_data.sh 		bash import_data.sh [database_name] [port_number]		
				- Bash script which will setup an existing 
				  database for LOST and import legacy data
		  	  	- Takes a database name and port number for 
				  the database as arguments

create_tables.sql 	psql [database_name] < create_tables.sql
				- psql script to create all necessary tables
				  to track LOST personnel, facilities, and assets

import_data.py 		python3 import_data.sh [database_name] [port_number]
				- Python script to reformat lost legacy data to 
				  enable it to be assimilated into a database 
				  formatted by 'create_tables.sql'
			  	- Requires a specific set of OSNAP legacy data
				  downloaded automatically by import_data.sh

lost_input.py 		supporting module; should not be run				
				- General input functions to be utilized by 
				  import_data.py
			  	- Communicates with the database without relying
				  on a specific data set
