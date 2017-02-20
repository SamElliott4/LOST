import os
import pathlib
import json

path = pathlib.Path("/home/osnapdev/wsgi/lost_config.json")

with path.open() as file:
    config = json.load(file)
    database = config['database']['dbname']
    host = config['database']['dbhost']
    port = config['database']['dbport']
