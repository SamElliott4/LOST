Home directory for the LOST database

Files:
install_daemons.sh:
	clones/downloads the needed files to install postgres and apache, then installs both

preflight.sh:
	calls sql/import_data.sh, which initializes a database for lost, and imports legacy data
	migrates files to wsgi folder (NOT YET FUNCTIONAL)
