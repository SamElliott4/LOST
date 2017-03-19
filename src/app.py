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


############################
# web application structure

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        if check_credentials(request.form['username'], request.form['password']): # false if username does not exist or username and password do not match
            session['username'] = get_username(request.form['username']) # Use capitalization found in database, i.e. when user was created
            return redirect(url_for('dashboard'))
        else:
            send_alert('Invalid username or password', 'warning')
            return redirect(url_for('login')) 
    return render_template('login.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method=='POST':
        if user_exists(request.form['username']):
            if update_user(request.form['username'], request.form['password']):
                return "Updated credentials for user: {}".format(request.form['username'])
            else:
                return "User exists, but credentials could not be updated"
        else:
            if add_user(request.form['username'], request.form['password'], request.form['role']):
                return "Created new user: {}".format(request.form['username'])  
            else:
                return "Unable to create new user"
    return redirect(url_for('login')) # I'd rather redirect away instead of crashing if a person navigates here in a browser

@app.route('/revoke_user', methods=['GET','POST'])
def revoke_user():
    if request.method == 'POST':
        if not user_exists(request.form['username']):
            return 'User does not exist'
        if deactivate_user(request.form['username']):
            return "Successfully deactivated user: {}".format(request.form['username'])
        else:
            return "User does not exist"
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
    populate_dashboard()
    return render_template('dashboard.html')

@app.route('/add_facility', methods=['GET', 'POST'])
def add_facility():
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
    if not has_authority(session['username'], 'Add Facility'):
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
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
    if not has_authority(session['username'], "Add Asset"):
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
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
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
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
    if not has_authority(session['username'], "Dispose Asset"):
        send_alert('You do not have authorization to perform this action', 'warning')
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
    # build asset table
    session['assets'] = get_assets()
    # get facilities available for new asset form
    cur.execute("SELECT f_code FROM facilities;")
    session['facilities'] = [f[0] for f in cur.fetchall()] 
    return render_template('dispose_asset.html')

@app.route('/transfer_req', methods=['GET', 'POST'])
def transfer_req():
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
    if not has_authority(session['username'], 'Transfer Request'):
        send_alert('You do not have authorization to perform this action', 'warning')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if make_transfer_request(session['username'], request.form['asset_tag'], request.form['dest'], datetime.datetime.utcnow().isoformat()):
            send_alert('Created new transfer request', 'success')
        else:
            send_alert('Unable to submit transfer request', 'warning')
        return redirect(url_for('transfer_req'))
    session['assets'] = get_assets()
    for i in range(len(session['assets'])):
        if session['assets'][i][5] != 'Active':
            session['assets'][i] = None
    while None in session['assets']:
        session['assets'].remove(None)
    cur.execute("SELECT f_code FROM facilities;")
    session['facilities'] = [f[0] for f in cur.fetchall()]
    return render_template('transfer_request.html')

@app.route('/approve_req', methods=['GET', 'POST'])
def approve_req():
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
    if not has_authority(session['username'], "Approve Transfer"):
        send_alert('You do not have authorization to perform this action', 'warning')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if request.form['action'] == 'Approve':
            if approve_transfer_request(session['req_id'], session['username'], datetime.datetime.utcnow().isoformat()):
                send_alert('Transfer request approved', 'success')
                for r in session['conflicts']:
                    reject_transfer_request(r[0], session['username'], datetime.datetime.utcnow().isoformat());
            else:
                send_alert('Unable to approve request', 'warning')
        elif request.form['action'] == 'Reject':
            if reject_transfer_request(session['req_id'], session['username'], datetime.datetime.utcnow().isoformat()):
                send_alert('Transfer request rejected', 'success')
            else:
                send_alert('Unable to reject transfer request', 'warning')
        return redirect(url_for('dashboard'))
    session['req_id'] = request.args.get('req_id', '')
    # get info for approval form
    session['req'] = get_request_info(session['req_id'])
    # reject all other pending requests for this asset
    session['conflicts'] = []
    cur.execute("""SELECT request_id FROM transfer_requests
            JOIN assets on asset_fk=asset_pk
            WHERE asset_tag=%s AND request_id!=%s AND approver IS NULL;""", (session['req'][1], session['req_id']))
    for r in cur.fetchall():
        session['conflicts'].append(get_request_info(r[0]))
    # replace previous requests not yet used
    cur.execute("""SELECT t.request_id FROM transfer_requests t
            JOIN asset_moving m on t.request_id = m.request_id
            JOIN assets a ON t.asset_fk = a.asset_pk
            WHERE m.load_dt IS NULL AND a.asset_tag=%s AND t.request_id!=%s;""", (session['req'][1], session['req_id']))
    for r in cur.fetchall():
        session['conflicts'].append(get_request_info(r[0]))
    return render_template('approve_req.html')

@app.route('/update_transit', methods=['GET', 'POST'])
def update_transit():
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
    if not has_authority(session['username'], 'Update Transit'):
        send_alert('You do not have authorization to perform this action', 'warning')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if 'load_time' in request.form:
            load_dt = convert_date(request.form['load_time']) if len(request.form['load_time']) > 0 else datetime.datetime.utcnow().isoformat()
            if update_transit(session['req_id'], load_time=load_dt):
                send_alert('Updated tracking information', 'success')
            else:
                send_alert('Unable to update tracking information', 'warning')
        if 'unload_time' in request.form:
            unload_dt = convert_date(request.form['unload_time']) if len(request.form['unload_time']) > 0 else datetime.datetime.utcnow().isoformat()
            if update_transit(session['req_id'], unload_time=unload_dt):
                send_alert('Updated tracking information', 'success')
            else:
                send_alert('Unable to update tracking information', 'warning')
        return redirect(url_for('dashboard'))
    session['req_id'] = request.args.get('req_id', '')
    session['transit'] = get_transfer_info(session['req_id'])
    return render_template('update_transit.html')

@app.route('/transfer_report', methods=['GET', 'POST'])
def transfer_report():
    if not verify_user():
        send_alert('You are not logged in', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['date'] != "":
            dt = convert_date(request.form['date'])
            # Handle rejected time format
            if dt is None:
                send_alert('Unrecognized date format', 'warning')
                return redirect(request.path)
        else:
            dt = datetime.datetime.utcnow().isoformat()
        session['transfer_report'] = filter_transfers(dt)
        return redirect(url_for('transfer_report'))
    return render_template('transfer_report.html')

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

def check_credentials(username, password):
    # returns true if user is able to log in
    # False if user is inactive
    # False if user entered incorrect credentials
    cur.execute("SELECT password, active FROM users WHERE user_id=%s;", [username.lower(),])
    cred = cur.fetchone()
    if cred is None: # No users with given username
        return False
    if not cred[1]: # User is inactive
        return False
    if cred[0] == password: # Passwords match
        return True
    return False

def add_user(username, password, role):
    # returns true if user is successfully created, false otherwise
    if user_exists(username):
        return False
    user_id = username.lower()
    h_pass = get_hash(password)
    role_fk = get_key('roles', 'role', role)
    try:
        cur.execute("""INSERT INTO users (user_id, username, password, role_fk, active) 
                VALUES (%s, %s, %s, %s, %s);""",[user_id, username, password, role_fk, True])
    except:
        db.rollback()
        return False
    db.commit()
    return True

def deactivate_user(username):
    user_id = username.lower()
    try:
        cur.execute("UPDATE users SET active=%s WHERE user_id=%s;", (False, user_id))
    except:
        db.rollback()
        return False
    db.commit()
    return True

def update_user(username, password):
    user_id = username.lower()
    try:
        cur.execute("UPDATE users SET password=%s, active=%s WHERE user_id=%s;", (password, True, user_id))
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
        asset_key = get_key('assets', 'asset_tag', asset_tag) #cur.fetchone()[0]
        fac_key = get_key('facilities', 'f_code', fcode) #cur.fetchone()[0]
        # New row in asset_at table
        cur.execute("""INSERT INTO asset_at (asset_fk, facility_fk, intake_dt) 
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
        # Update necessary information
        # Facility information needs to remain intact for historical reference
        cur.execute("UPDATE assets SET status=0 WHERE asset_tag=%s;", (asset_tag,))
        cur.execute("UPDATE asset_at SET expunge_dt=%s WHERE asset_fk=%s;", (datetime, asset_key))
    except:
        db.rollback()
        return False
    db.commit()
    return True

def make_transfer_request(username, asset_tag, destination, date):
    cur.execute("SELECT user_id FROM users WHERE username=%s;", (username,))
    user = cur.fetchone()[0]
    cur.execute("""SELECT facility_pk, f_code FROM facilities 
            JOIN asset_at ON facility_pk=facility_fk 
            JOIN assets ON asset_fk=asset_pk 
            WHERE asset_tag=%s AND expunge_dt IS NULL;""", (asset_tag,))
    src, src_code = cur.fetchone()
    cur.execute("SELECT facility_pk FROM facilities WHERE f_code=%s;", (destination,))
    dest = cur.fetchone()[0]
    if src == dest: # No transfer requests to and from same facility
        return False
    asset_key = get_key('assets', 'asset_tag', asset_tag)
    cur.execute("SELECT * FROM transfer_requests;")
    req_num = len(cur.fetchall()) + 1
    try:
        cur.execute("""INSERT INTO transfer_requests (request_id, requester, asset_fk, src, dest, request_dt, status) 
                VALUES (%s, %s, %s, %s, %s, %s, 0);""", (src_code + str(req_num), user, asset_key, src, dest, date))
    except:
        db.rollback()
        return False
    db.commit()
    return True

def approve_transfer_request(req_id, username, date):
    user = get_key('users', 'username', username)
    cur.execute("SELECT asset_fk, src, dest FROM transfer_requests WHERE request_id=%s;", (req_id,))
    asset_key, src, dest = cur.fetchone()
    try:
        cur.execute("UPDATE transfer_requests SET approver=%s, approve_dt=%s, status=1 WHERE request_id=%s;", (user, date, req_id))
        cur.execute("INSERT INTO asset_moving (request_id, asset_fk, src, dest) VALUES (%s, %s, %s, %s);", (req_id, asset_key, src, dest))
    except:
        db.rollback()
        return False
    db.commit()
    return True

def reject_transfer_request(req_id, username, date):
    user = get_key('users', 'username', username)
    try:
        cur.execute("UPDATE transfer_requests SET approver=%s, approve_dt=%s, status=-1 WHERE request_id=%s;", (user, date, req_id))
        # Remove any canceled requests from asset_moving table
        cur.execute("DELETE FROM asset_moving WHERE request_id=%s;", (req_id,))
    except:
        db.rollback()
        return False
    db.commit()
    return True

def update_transit(req_id, load_time=None, unload_time=None):
    cur.execute("SELECT asset_fk FROM asset_moving WHERE request_id=%s;", (req_id,))
    asset_key = cur.fetchone()[0]
    if load_time is not None:
        try:
            cur.execute("UPDATE asset_moving SET load_dt=%s WHERE request_id=%s;", (load_time, req_id))
            cur.execute("UPDATE assets SET status=2 WHERE asset_pk=%s;", (asset_key,))
            cur.execute("UPDATE asset_at SET expunge_dt=%s WHERE asset_fk=%s AND expunge_dt IS NULL;", (load_time, asset_key))
        except:
            db.rollback()
            return False
    if unload_time is not None:
        cur.execute("SELECT dest FROM asset_moving WHERE request_id=%s;", (req_id,))
        fac_key = cur.fetchone()[0]
        try:
            cur.execute("UPDATE asset_moving SET unload_dt=%s WHERE request_id=%s;", (unload_time, req_id))
            cur.execute("UPDATE assets SET status=1 WHERE asset_pk=%s;", (asset_key,))
            cur.execute("INSERT INTO asset_at (asset_fk, facility_fk, intake_dt) VALUES (%s, %s, %s);", (asset_key, fac_key, unload_time))
        except:
            db.rollback()
            return False
    db.commit()
    return True

def get_assets():
    # returns a list of lists of the format [asset_tag, description, fcode, intake_date, expunge_date, status]
    assets = []
    cur.execute("SELECT asset_pk FROM assets WHERE status>0;")
    asset_list = [a[0] for a in cur.fetchall()]
    for a in asset_list: # We only want one row for each asset
        cur.execute("""SELECT asset_tag, description, f_code, intake_dt, expunge_dt, status FROM assets
                JOIN asset_at ON asset_pk=asset_fk
                JOIN facilities ON facility_fk=facility_pk
                WHERE asset_pk=%s;""", (a,))
        res = cur.fetchall()
        assets.append(list(sorted(res, key=lambda res: res[3], reverse=True)[0])) # sort by intake date, choose latest entry
    for a in assets:
        # trim date values
        a[3] = str(a[3]).split('.')[0]
        if a[4] is not None:
            a[4] = str(a[4]).split('.')[0]
        # clear facility entry if asset is in transit
        if a[5] == 2:
            a[2] = ""
        # convert status to text
        status = {0: 'Inactive', 1: 'Active', 2: 'In transit'}
        a[5] = status[a[5]]
    return assets

def filter_assets(fcode, date):
    # returns a list a assets for a given facility on a given date
    # Fix date to properly include assets taken in on the selected day
    dt = date.split("T")
    dt = dt[0] + "T23:59:59"
    cur.execute("""SELECT asset_tag, description, f_code, intake_dt, expunge_dt, status FROM assets 
            JOIN asset_at ON asset_pk=asset_fk 
            JOIN facilities on facility_fk=facility_pk 
            WHERE f_code like %s 
            AND intake_dt <= %s 
            AND (expunge_dt is null OR NOT expunge_dt < %s)
            ;""", (fcode+'%', dt, date))
    assets = [[a[0], a[1], a[2], a[3], a[4], a[5]] for a in cur.fetchall()]
    for a in assets:
        if a[3] is not None:
            a[3] = str(a[3]).split(".")[0]
        if a[4] is not None:
            a[4] = str(a[4]).split(".")[0]
        # convert status to text
        status = {0: 'Inactive', 1:'Active', 2:'In transit'}
        a[5] = status[a[5]]
    return assets

def filter_transfers(date):
    # returns a list of assets in transit on a given day.
    dt = date.split("T")
    dt = dt[0] + "T23:59:59"
    cur.execute("""SELECT asset_tag, description, src, dest, load_dt, unload_dt FROM asset_moving
            JOIN assets ON asset_fk=asset_pk
            WHERE load_dt <= %s AND (unload_dt IS NULL OR NOT unload_dt < %s);""", (dt, date))
    assets = [[a[0], a[1], a[2], a[3], a[4], a[5]] for a in cur.fetchall()]
    for a in assets:
        # fetch fcodes for origin and destination
        cur.execute("SELECT f_code FROM facilities WHERE facility_pk=%s;", (a[2],))
        a[2] = cur.fetchone()[0]
        cur.execute("SELECT f_code FROM facilities WHERE facility_pk=%s;", (a[3],))
        a[3] = cur.fetchone()[0]
        # strip <second units from timestamp, if any; if entry is NULL, replace with empty string
        a[4] = str(a[4]).split(".")[0] if a[4] is not None else ""
        a[5] = str(a[5]).split(".")[0] if a[5] is not None else ""
    return assets

def verify_user():
    # Returns False if no user is logged in, True otherwise
    if 'username' not in session:
        session['clear'] # If no user, we don't want any other info either
        return False
    return True

def get_capabilities(username):
    # returns a list of capability keys corresponding to what a user is authorizaed to do
    cur.execute("""SELECT capability_fk FROM has 
            WHERE role_fk=(SELECT role_fk FROM users WHERE user_id=%s);""",(username.lower(),))
    cap_list = [i[0] for i in cur.fetchall()]
    return cap_list

def has_authority(username, action):
    # returns True if a user is able to perform a given action, False, otherwise
    cur.execute("SELECT capability_pk FROM capabilities WHERE capability=%s;",(action,))
    output = cur.fetchone()
    # avoid index error if query returned None
    action_key = output[0] if output != None else None
    cap_list = get_capabilities(username)
    if action_key in cap_list:
        return True
    return False

def populate_dashboard():
    if 'username' not in session:
        return
    # set users role
    username = session['username']
    cur.execute("""SELECT role FROM roles JOIN users on role_pk=role_fk 
            WHERE user_id=%s;""", (username.lower(),))
    session['role'] = cur.fetchone()[0]
    # build task set
    session['tasks'] = []
    cap_list = get_capabilities(username)
    capabilities = {  # All capabilities that have links in the dashboard
            'Add Facility': 'add_facility', 
            'Add Asset': 'add_asset', 
            'Dispose Asset': 'dispose_asset', 
            'Transfer Request': 'transfer_req',
    }
    action_items = { # All pending actions that may require user's attention
            'Approve Transfer': 'approve_req',
            'Update Transit': 'update_transit'
    }
    pending = []
    for i in cap_list:
        # add tuple of (capability, route) for each capability
        cur.execute("SELECT capability FROM capabilities WHERE capability_pk=%s ;",(i,))
        c = cur.fetchone()[0]
        if c in capabilities:
            session['tasks'].append((c, capabilities[c]))
        if c in action_items:
            pending.append(c)
    # Items awaiting attention table
    for a in pending:
        if a == 'Approve Transfer':
            session['pending_requests'] = []
            cur.execute("""SELECT request_id FROM transfer_requests WHERE approver IS NULL;""")
            for r in cur.fetchall():
                session['pending_requests'].append(get_request_info(r[0]))
        if a == 'Update Transit':
            session['pending_transfers'] = []
            cur.execute("""SELECT request_id FROM asset_moving
                    WHERE load_dt IS NULL OR unload_dt IS NULL""")
            for r in cur.fetchall():
                if r[0]:
                    session['pending_transfers'].append(get_transfer_info(r[0]))

def send_alert(message, color):
    alerts = {'warning':'#F88080', 'success':'#80F880'}
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

def get_request_info(req_id):
    cur.execute("SELECT request_id, asset_fk, src, dest, request_dt FROM transfer_requests WHERE request_id=%s;", (req_id,))
    req = cur.fetchone()
    cur.execute("SELECT asset_tag, description FROM assets WHERE asset_pk=%s;", (req[1],))
    asset_tag, description = cur.fetchone()
    cur.execute("SELECT f_code FROM facilities WHERE facility_pk=%s;", (req[2],))
    src = cur.fetchone()[0]
    cur.execute("SELECT f_code FROM facilities WHERE facility_pk=%s;", (req[3],))
    dest = cur.fetchone()[0]
    dt = str(req[4]).split(".")
    return [req[0], asset_tag, description, src, dest, dt[0]]

def get_transfer_info(req_id):
    cur.execute("SELECT asset_fk, src, dest, load_dt, unload_dt FROM asset_moving WHERE request_id=%s;", (req_id,))
    t = cur.fetchone()
    cur.execute("SELECT asset_tag, description FROM assets WHERE asset_pk=%s;", (t[0],))
    asset_tag, description = cur.fetchone()
    cur.execute("SELECT f_code FROM facilities WHERE facility_pk=%s;", (t[1],))
    src = cur.fetchone()[0]
    cur.execute("SELECT f_code FROM facilities WHERE facility_pk=%s;", (t[2],))
    dest = cur.fetchone()[0]
    # Trim displayed time of anything smaller than seconds
    load_dt = t[3]
    if load_dt is not None:
        load_dt = str(load_dt).split(".")[0]
    else:
        load_dt = ""
    unload_dt = t[4]
    if unload_dt is not None:
        unload_dt = str(unload_dt).split(".")[0]
    else:
        unload_dt = ""
    return [req_id, asset_tag, description, src, dest, load_dt, unload_dt]


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
