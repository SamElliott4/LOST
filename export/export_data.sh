# vim: background=dark

if [ $# -ne 2 ]; then
	echo "Usage: ./export_data.sh <dbname> (output dir>"
	exit;
fi

dbname=$1
dir=$2

# following line borrowed from stackoverflow
cpath="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# prep target directory
if [ ! -d $dir ]; then
	mkdir $dir
else
	read -p "Okay to clear contents of $dir?  y or n  " resp
	if [ $resp == y ]; then
		rm -r $dir/*
	else
		echo "Aborting"
	fi
fi

cd $dir
output=$PWD
# prep csv files
echo "username,password,role,active" > users.csv
echo "fcode,common_name" > facilities.csv
echo "asset_tag,description,facility,acquired,disposed" > assets.csv
echo "asset_tag,request_by,request_dt,approve_by,approve_dt,source,destination,load_dt,unload_dt" > transfers.csv

# Read db contents and migrate data to csv files
cd $cpath
python3 export_data.py $dbname $output

echo "Data written to $output"
