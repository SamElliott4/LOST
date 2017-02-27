# vim: background=dark

import hashlib
import psycopg2
import datetime
from flask import Flask, url_for, request, render_template, redirect, session, flash
from config import database, host, port

app = Flask(__name__)
app.secret_key = 'the secret key is "secret key"'

db = psycopg2.connect(dbname=database, host=host, port=port)
cur = db.cursor()

# global variables
ALERT = {'warning':'#F88080', 'success':'#80F880'}


############################
# web application structure

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        if compare_password(request.form['username'], request.form['password']): # false if username does not exist or username and password do not match
            session['username'] = get_username(request.form['username']) # Use capitalization found in database, i.e. when user was created
            return redirect(url_for('dashboard'))
        else:
            send_alert('Invalid username or password', 'warning')
            return redirect(url_for('login')) 
    return render_template('login.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method=='POST':
        # add_user checks for existing usernames, aborts and returns false if one is found
        if add_user(request.form['username'], request.form['password'], request.form['role']):
            send_alert('Successfully created new user', 'success')
            return redirect(url_for('login'))    
        else:
            send_alert('Username already exists', 'warning')
            return redirect(url_for('create_user'))
    cur.execute("SELECT title FROM roles;")
    session['roles'] = cur.fetchall()
    return render_template("create_user.html")

@app.route('/dashboard', methods=['GET'])
def dashboard():
    verify_user()
    populate_dashboard()
    return render_template('dashboard.html')

@app.route('/add_facility', methods=['GET', 'POST'])
def add_facility():
    verify_user()
    if not has_authority(session['username'], 'add facility'):
        send_alert('You do not have authorization to perform this action', 'warning')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if add_facility(request.form['fcode'], request.form['name']):
            send_alert('Added new facility', 'success')
        else:
            send_alert('Failed to add facility', 'warning')
        return redirect(url_for('add_facility'))
    cur.execute("SELECT f_code, common_name FROM facilities;")
    session['facilities'] = [(f[0], f[1]) for f in cur.fetchall()]
    return render_template("add_facility.html")

@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    verify_user()
    if not has_authority(session['username'], "add asset"):
        send_alert('You do not have authorization to perform this action', 'warning')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if request.form['date'] != "":
            dt = convert_date(request.form['date'])
            # Handle rejected date format
            if dt is None:
                send_alert('Unrecognized date format', 'warning')
                return redirect(request.path)
        else:
            dt = datetime.datetime.utcnow().isoformat()
        if add_asset(request.form['asset_tag'], request.form['description'], request.form['facility'], dt):
            send_alert('Added new asset', 'success')
        else:
            send_alert('Failed to add asset', 'warning')
        return redirect(url_for('add_asset'))
    # Build Asset table
    session['assets'] = get_assets()
    # get facilities available for new asset form
    cur.execute("SELECT f_code FROM facilities;")
    session['facilities'] = [f[0] for f in cur.fetchall()]
    return render_template("add_asset.html")

@app.route('/asset_report', methods=['GET', 'POST'])
def asset_report():
    verify_user()
    if request.method == 'POST':
        if request.form['date'] != "":
            dt = convert_date(request.form['date'])
            # Handle rejected time format
            if dt is None:
                send_alert('Unrecognized date format', 'warning')
                return redirect(request.path)
        else:
            dt = datetime.datetime.utcnow().isoformat()
        session['asset_report'] = filter_assets(request.form['facility'], dt)
        return redirect(url_for('asset_report'))
    cur.execute("SELECT f_code FROM facilities;")
    session['facilities'] = [f for f in cur.fetchall()]
    return render_template("asset_report.html")

@app.route('/dispose_asset', methods=['GET', 'POST'])
def dispose_asset():
    verify_user()
    if not has_authority(session['username'], "dispose asset"):
        send_alert('You do not has authorization to perform this action', 'warning')
        return redirect(url_for('dashboard'))
    if request.method=='POST':
        if request.form['date'] != "":
            dt = convert_date(request.form['date'])
            # Handle rejected time format
            if dt is None:
                send_alert('Unrecognized date format', 'warning')
                return redirect(request.path)
        else:
            dt = datetime.datetime.utcnow().isoformat()
        if dispose_asset(request.form['asset_tag'], dt):
            send_alert('Successfully disposed asset', 'success')
        else:
            send_alert('Failed to dispose asset', 'warning')
        return redirect(url_for('dispose_asset'))
    # Build Asset table
    session['assets'] = get_assets()
    # get facilities available for new asset form
    cur.execute("SELECT f_code FROM facilities;")
    session['facilities'] = [f[0] for f in cur.fetchall()] 
    return render_template('dispose_asset.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


#######################
# supporting functions

def get_username(username):
    # Returns username if one exists, None otherwise
    cur.execute("SELECT username FROM users WHERE user_id=%s;",[username.lower(),])
    user = cur.fetchone()
    return user if user is None else user[0]

def user_exists(username):
    # Returns True is user exists, False otherwise
    return get_username(username) is not None

def compare_password(username, password):
    # returns true if username and password match, false otherwise
    h_pass = get_hash(password)
    cur.execute("SELECT password FROM users WHERE user_id=%s;", [username.lower(),])
    pword = cur.fetchone()
    if pword is None:
        return False
    if pword[0] == h_pass:
        return True
    return False

def add_user(username, password, role):
    # returns true if user is successfully created, false otherwise
    if user_exists(username):
        return False
    user_id = username.lower()
    h_pass = get_hash(password)
    role_fk = get_key('roles', 'title', role)
    try:
        cur.execute("""INSERT INTO users (user_id, username, password, role_fk) 
                VALUES (%s, %s, %s, %s);""",[user_id, username, h_pass, role_fk])
    except:
        db.rollback()
        return False
    db.commit()
    return True

def add_facility(fcode, common_name):
    try:
        cur.execute("""INSERT INTO facilities (f_code, common_name) 
                VALUES (%s, %s);""", (fcode.upper(), common_name))
    except:
        db.rollback()
        return False
    db.commit()
    return True


def add_asset(asset_tag, description, fcode, date):
    # atomically add a new asset (e.g. if insertion into asset_at fails, nothing is added to asset table)
    # aborts and returns False if any insertion fails, True otherwise
    try:
        # New row in assets table; new assets are automatically assumed to be active
        cur.execute("INSERT INTO assets (asset_tag, description, status) VALUES (%s, %s, 1);", (asset_tag, description))
        # get asset_pk and facility_pk
        #cur.execute("SELECT asset_pk FROM assets WHERE asset_tag=%s;", (asset_tag,))
        asset_key = get_key('assets', 'asset_tag', asset_tag) #cur.fetchone()[0]
        #cur.execute("SELECT facility_pk FROM facilities WHERE f_code=%s;", (fcode,))
        fac_key = get_key('facilities', 'f_code', fcode) #cur.fetchone()[0]
        # New row in asset_at table
        cur.execute("""INSERT INTO asset_at (asset_fk, facility_fk, intake_date) 
                VALUES (%s, %s, %s);""", (asset_key, fac_key, date))
    except:
        db.rollback()
        return False
    db.commit()
    return True

def dispose_asset(asset_tag, datetime):
    # atomically dispose an existing asset
    # returns true if asset successfully disposed, false otherwise
    try:
        # Ensure selected asset is active
        cur.execute("SELECT status FROM assets WHERE asset_tag=%s;", (asset_tag,))
        assert(cur.fetchone()[0] == 1)
        # Get asset_pk
        asset_key = get_key('assets', 'asset_tag', asset_tag)
        #cur.execute("SELECT asset_pk FROM assets WHERE asset_tag=%s;", (asset_tag,))
        #asset_key = cur.fetchone()[0]
        # Update necessary information
        # Facility information needs to remain intact for historical reference
        cur.execute("UPDATE assets SET status=0 WHERE asset_tag=%s;", (asset_tag,))
        cur.execute("UPDATE asset_at SET expunge_date=%s WHERE asset_fk=%s;", (datetime, asset_key))
    except:
        db.rollback()
        return False
    db.commit()
    return True

def get_assets():
    # returns a list of lists of the format [asset_tag, description, fcode, intake_date, expunge_date, status]
    #TODO merge get_assets and filter_assets
    cur.execute("""SELECT asset_tag, description, f_code, intake_date, expunge_date, status FROM assets 
            JOIN asset_at ON asset_pk=asset_fk 
            JOIN facilities on facility_fk=facility_pk ;""")
    assets = [[a[0], a[1], a[2], a[3], a[4], a[5]] for a in cur.fetchall()]
    for a in assets:
        #TODO handle multple asset_at entries for the same asset
        # trim date values
        if a[3] is not None:
            a[3] = str(a[3]).split(".")[0]
        if a[4] is not None:
            a[4] = str(a[4]).split(".")[0]
            a[2] = ""
        # convert status to text
        a[5] = "Active" if a[5] == 1 else "Inactive"
    return assets

def filter_assets(fcode, date):
    # returns a list a assets for a given facility on a given date

    # Fix date to properly include assets taken in on the selected day
    dt = date.split("T")
    dt = dt[0] + "T23:59:59"
    print(dt)
    cur.execute("""SELECT asset_tag, description, f_code, intake_date, expunge_date, status FROM assets 
            JOIN asset_at ON asset_pk=asset_fk 
            JOIN facilities on facility_fk=facility_pk 
            WHERE f_code like %s 
            AND intake_date <= %s 
            AND (expunge_date is null OR NOT expunge_date < %s)
            ;""", (fcode+'%', dt, date))
    assets = [[a[0], a[1], a[2], a[3], a[4], a[5]] for a in cur.fetchall()]
    for a in assets:
        if a[3] is not None:
            a[3] = str(a[3]).split(".")[0]
        if a[4] is not None:
            a[4] = str(a[4]).split(".")[0]
        # convert status to text
        a[5] = "Active" if a[5] == 1 else "Inactive"
    return assets

    # WHERE intake_date <= date AND (expunge_date is null OR NOT expunge_date < %s)

def verify_user():
    # Kicks back to login page if no user is logged in
    if 'username' not in session:
        flash('you are not logged in')
        session['alert'] = ALERT['warning']
        return redirect(url_for('login'))
    return

def get_capabilities(username):
    cur.execute("""SELECT capability_fk FROM has 
            WHERE role_fk=(SELECT role_fk FROM users WHERE user_id=%s);""",(username.lower(),))
    cap_list = [i[0] for i in cur.fetchall()]
    return cap_list


def has_authority(username, action):
    cur.execute("SELECT capability_pk FROM capabilities WHERE name=%s;",(action,))
    output = cur.fetchone()
    # avoid index error if query returned None
    action_key = output[0] if output != None else None
    cap_list = get_capabilities(username)
    if action_key in cap_list:
        return True
    return False

def populate_dashboard():
    if not session['username']:
        return
    # set users role
    username = session['username']
    cur.execute("""SELECT title FROM roles JOIN users on role_pk=role_fk 
            WHERE user_id=%s;""", (username.lower(),))
    session['role'] = cur.fetchone()[0]
    # build task set
    session['tasks'] = []
    cap_list = get_capabilities(username)
    for i in cap_list:
        # add tuple of (name, route) for each capability
        cur.execute("SELECT name FROM capabilities WHERE capability_pk=%s ;",(i,))
        c = cur.fetchone()[0]
        session['tasks'].append((c,c.replace(" ", "_")))

def send_alert(message, color):
    alerts = {'warning':'#F88080', 'success':'80F880'}
    flash(message)
    session['alert'] = alerts[color] if color in alerts.keys() else color

def get_hash(string):
    return hashlib.sha256(string.encode()).hexdigest()

def get_key(table, field, value):
    #Fetches a primary key from provided table where table.field = value
    cur.execute("""SELECT column_name FROM information_schema.columns 
            WHERE table_name=%s;""", (table,))
    keyType = cur.fetchone()[0]
    cur.execute("SELECT " + keyType + " FROM " + table + " WHERE " + field + "='" + value + "';")
    output = cur.fetchone()
    key = output[0] if output is not None else None
    return key

def convert_date(date):
    # Currently only supports yyyy-mm-dd (hh:mm:ss) format
    # any of hh, mm, ss may be omitted, but smaller units are assumed to be omitted first
    try:
        # Substitube any likely special characters
        dt = date.replace("-", " ")
        dt = dt.replace(":", " ")
        dt = dt.replace("/", " ")
        # Split date string to check contents
        dt = dt.split(" ")
        assert(len(dt) >= 3)
        if len(dt) < 6:
            for i in range(6-len(dt)):
                #pad out omitting time info
                dt.append("00")
        # Rejoin date into string
        dt = " ".join(dt)
        dt = datetime.datetime.strptime(dt, '%Y %m %d %H %M %S').isoformat()
    except:
        return None
    return dt


# run the web app when program is called
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
