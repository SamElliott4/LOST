import psycopg2

DB = None
cur = None

def connectDB(database, portNum ):
    global DB 
    global cur
    DB = psycopg2.connect(dbname=database , host="/tmp/", port=portNum)
    cur = DB.cursor()


def commitChanges():
    DB.commit()

#Asset Tables
def newProduct(vendor, desc, alt_desc):
    if DB is None:
        return
    cur.execute("INSERT INTO products (vendor, description, alt_description) VALUES (%s, %s, %s);", (vendor, desc, alt_desc))
    DB.commit()

def newFacility(fcode, name, location):
    if DB is None:
        return
    cur.execute("INSERT INTO facilities (fcode, common_name, location) VALUES (%s, %s, %s);", (fcode, name, location))
    DB.commit()

def newAsset(product_key, asset_tag, desc, alt_desc):
    if DB is None:
        return
    cur.execute("INSERT INTO assets (product_fk, asset_tag, description, alt_description) VALUES (%s, %s, %s, %s);", (product_key, asset_tag, desc, alt_desc))
    DB.commit()

def newConvoy(request, source, dest, depart, arrive):
    if DB is None:
        return
    cur.execute("INSERT INTO convoys (request, source_fk, dest_fk, depart_dt, arrive_dt) VALUES (%s, %s, %s, %s, %s);", (request, source, dest, depart, arrive))
    DB.commit()

def newVehicle(asset_key):
    if DB is None:
        return
    cur.execute("INSERT INTO vehicles (asset_fk) VALUES (%s);", (asset_key,))
    DB.commit()

def newAssetAt(asset_key, facility_key, arrive, depart):
    if DB is None:
        return
    cur.execute("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt, depart_dt) VALUES (%s, %s, %s, %s);", (asset_key, facility_key, arrive, depart))
    DB.commit()

def newAssetOn(asset_key, convoy_key, load, unload):
    if DB is None:
        return
    cur.execute("INSERT INTO asset_on (asset_fk, convoy_fk, load_dt, unload_dt) VALUES (%s, %s, %s, %s);", (asset_key, convoy_key, load, unload))
    DB.commit()

def newUsedBy(vehicle_key, convoy_key):
    if DB is None:
        return
    cur.execute("INSERT INTO used_by (vehicle_fk, convoy_fk) VALUES (%s, %s);", (vehicle_key, convoy_key))
    DB.commit()

#User Tables
def newUser():
    if DB is None:
        return


def newRole():
    if DB is None:
        return

#Security Tables
def newLevel(abbrv, comment):
    if DB is None:
        return
    cur.execute("INSERT INTO levels (abbrv, comment) VALUES (%s, %s);", (abbrv, comment))
    DB.commit()

def newCompartment(abbrv, comment):
    if DB is None:
        return
    cur.execute("INSERT INTO compartments (abbrv, comment) VALUES (%s, %s);", (abbrv, comment))
    DB.commit()

def newTag(level, comp, user, product, asset):
    if DB is None:
        return
    #must have user xor product xor asset

    cur.execute("INSERT INTO security_tags (level_fk, compartment_fk, user_fk, product_fk, asset_fk) VALUES (%s, %s, %s, %s, %s);", (level, comp, user, product, asset))
    DB.commit()

#Fetch primary keys
def getKey(table, field, value):
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s;", (table,))
    keyType = cur.fetchone()[0]
    cur.execute("SELECT " + keyType + " FROM " + table + " WHERE " + field + "='" + value + "';")
    key = cur.fetchone()[0]
    return key

