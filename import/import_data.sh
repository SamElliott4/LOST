# vim: background=dark

if [ "$#" -ne 2 ]; then
	echo "Usage: ./import_data.sh <dbname> <import dir>"
	exit;
fi

dbname=$1
dir=$2
cpath="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# ensure $dir is an absolute path in case navigation to cpath would break a relative path
cd $dir
dir=$PWD

cd $cpath
python3 import_data.py $dbname $dir
