

cd $HOME
mkdir $1

git clone https://github.com/postgres/postgres.git
cd postgres
git checkout -b REL9_5_STABLE origin/REL9_5_STABLE
./configure --prefix=$1
make
make install

cd $HOME
curl www-us.apache.org/dist/httpd/httpd-2.4.25.tar.gz | tar xvz
cd httpd-2.4.25
./configure --prefix=$1
make
make install
