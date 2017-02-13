from flask import Flask, url_for, request, render_template, redirect, session
import psycopg2
import json
import datetime
app = Flask(__name__)
app.secret_key = 'flimsy key'
from config import database, host, port
db = psycopg2.connect(dbname=database, host=host, port=port)
cur = db.cursor()

################################################################
# Code for Assignment 5
#
# Visiting the addresses in a browset will perform a GET request
# Which will return an API stub with example arguments filled in
# (Built as dict ex in most functions)
#
# navigating to the addresses with a POST request will(would) 
# make the API call

@app.route('/rest', methods=['GET', 'POST'])
def welcome():
    session['example'] = ''
    return render_template('api_info.html', name=None)

@app.route('/rest/lost_key', methods=['POST','GET'])
def lost_key():
    if request.method=='POST':
        data = {}
        data['timestamp'] = datetime.datetime.utcnow().isoformat()
        data['key'] = 'OpenSesame'
        data['result'] = 'OK'
        return json.dumps(data)
    return render_template('api_stub.html')

@app.route('/rest/activate_user', methods=['POST','GET'])
def activate_user():
    if request.method=='POST' and 'arguments' in request.form:
        req=json.loads(request.form['arguments'])
        data = {}
        data['timestamp'] = req['timestamp']
        data['result'] = 'OK'
        return json.dumps(data)
    ex = {'timestamp': datetime.datetime.utcnow().isoformat(),
            'username': 'Wilson'
    }
    session['example'] = json.dumps(ex)
    return render_template('api_stub.html')

@app.route('/rest/suspend_user', methods=['POST','GET'])
def suspend_user():
    if request.method=='POST' and 'arguments' in request.form:
        req=json.loads(request.form['arguments'])
        data = {}
        data['timestamp'] = req['timestamp']
        data['result'] = 'OK'
        return json.dumps(data)
    ex = {'timestamp': datetime.datetime.utcnow().isoformat(),
            'username': 'Hodor'
    }
    session['example'] = json.dumps(ex)
    return render_template('api_stub.html')

@app.route('/rest/list_products', methods=['POST','GET'])
def list_products():
    if request.method=='POST' and 'arguments' in request.form:
        req=json.loads(request.form['arguments'])
        data = {}
        data['timestamp'] = req['timestamp']
        data['listing'] = [
                {
                    'vendor': 'Dunder Mifflin',
                    'description': 'LOST legal size notepad',
                    'compartments': ''
                },
                {
                    'vendor': 'big n large',
                    'description': 'LOST legal size notepad',
                    'compartments': ''
                }
        ]
        return json.dumps(data)
    ex = {'timestamp': datetime.datetime.utcnow().isoformat(),
            'vendor': '',
            'description': 'notepad',
            'compartments': []
    }
    session['example'] = json.dumps(ex)
    return render_template('api_stub.html')

@app.route('/rest/suspend_user', methods=['POST','GET'])
def suspend_user():
    if request.method=='POST' and 'arguments' in request.form:
        req=json.loads(request.form['arguments'])
        data = {}
        data['timestamp'] = req['timestamp']
        data['result'] = 'OK'
        return json.dumps(data)
    ex = {'timestamp': datetime.datetime.utcnow().isoformat(),
            'username': 'Hodor'
    }
    session['example'] = json.dumps(ex)
    return render_template('api_stub.html')

@app.route('/rest/list_products', methods=['POST','GET'])
def list_products():
    if request.method=='POST' and 'arguments' in request.form:
        req=json.loads(request.form['arguments'])
        data = {}
        data['timestamp'] = req['timestamp']
        data['listing'] = [
                {
                    'vendor': 'Dunder Mifflin',
                    'description': 'LOST legal size notepad',
                    'compartments': ''
                },
                {
                    'vendor': 'big n large',
                    'description': 'LOST legal size notepad',
                    'compartments': ''
                }
        ]
        return json.dumps(data)
    ex = {'timestamp': datetime.datetime.utcnow().isoformat(),
            'vendor': '',
            'description': 'notepad',
            'compartments': []
    }
    session['example'] = json.dumps(ex)
    return render_template('api_stub.html')

@app.route('/rest/add_products', methods=['POST','GET'])
def add_products():
    if request.method=='POST' and 'arguments' in request.form:
        req=json.loads(request.form['arguments'])
        data = {}
        data['timestamp'] = req['timestamp']
        data['result'] = 'OK'
        return json.dumps(data)
    ex = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'new_products': [
            {
                'vendor': 'Dunder Mifflin',
                'description': 'LOST letter size notepad',
                'alt_description': "Children's storybook",
                'compartments': ['adm:s']
            },
            {
                'vendor': 'Stark Industries',
                'description': 'Micronized Arc Reactor',
                'alt_description': 'Baseball',
                'compartments': ['nrg:ts', 'wpn:s']

            }
        ]
    }
    session['example'] = json.dumps(ex)
    return render_template('api_stub.html')

@app.route('/rest/add_asset', methods=['POST','GET'])
def add_asset():
    if request.method=='POST' and 'arguments' in request.form:
        req=json.loads(request.form['arguments'])
        data = {}
        data['timestamp'] = req['timestamp']
        data['result'] = 'OK'
        return json.dumps(data)
    ex = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'vendor': 'Dunder Mifflin',
            'description': 'LOST letter size notepad',
            'compartments': ['wpn:ts'],
            'facility': 'HQ'
        }
    session['example'] = json.dumps(ex)
    return render_template('api_stub.html')


###Code for assignment 3

@app.route('/', methods=['GET', 'POST'])
def login():
    session['report_url'] = url_for('report_filter')
    session['logout_url'] = url_for('logout')
    return render_template('login.html', name=None)

@app.route('/report', methods=['GET', 'POST',])
def report_filter():
    session['facility_url'] = url_for('facility_report')
    session['transit_url'] = url_for('transit_report')
    return render_template('report_filter.html')

@app.route('/report/facilities', methods=['GET', 'POST'])
def facility_report():
    start_date = request.args.get('sdate', '')
    end_date = request.args.get('edate', '')
    fcode = request.args.get('facility', '')
    if len(start_date) == 0:
        cur.execute("SELECT facility_fk, asset_tag, description, arrive_dt, depart_dt FROM assets JOIN asset_at ON asset_pk=asset_fk;")
        results = cur.fetchall()
    else:
        if len(end_date) == 0:
            end_date = start_date
        cur.execute("SELECT facility_fk, asset_tag, description, arrive_dt, depart_dt FROM assets JOIN asset_at ON asset_pk=asset_fk WHERE (NOT depart_dt < %s AND NOT arrive_dt > %s) OR (depart_dt is null AND arrive_dt <= %s);", (start_date, end_date, end_date))
        results = cur.fetchall()
    data = []
    for r in results:
        entry = ["", "", r[1], r[2], r[3], r[4]]
        cur.execute("SELECT fcode, common_name FROM facilities WHERE facility_pk=%s;", (r[0],))
        fac = cur.fetchone()
        if fac[0] == fcode or len(fcode) == 0:
            entry[0] = fac[0]
            entry[1] = fac[1]
            data.append(entry)
    session['fac_data'] = data
    return render_template('facility_report.html')

@app.route('/report/transit', methods=['GET', 'POST'])
def transit_report():
    start_date = request.args.get('sdate', '')
    end_date = request.args.get('edate', '')
    src_facility = request.args.get('src', '')
    dest_facility = request.args.get('dest', '')
    if len(start_date) == 0:
        cur.execute("SELECT source_fk, dest_fk, depart_dt, arrive_dt, request, asset_fk FROM convoys JOIN asset_on ON convoy_pk=convoy_fk;")
        results = cur.fetchall()
    else: 
        if len(end_date) == 0:
            end_date = start_date + ""
        end_date += " 23:59:59"
        start_date += " 00:00:00"
        cur.execute("SELECT source_fk, dest_fk, depart_dt, arrive_dt, request, asset_fk FROM convoys JOIN asset_on ON convoy_pk=convoy_fk WHERE NOT arrive_dt < %s AND NOT depart_dt > %s;", (start_date, end_date))
        results = cur.fetchall()
    data =[]
    for r in results:
        entry = ["", "", r[2], "", r[3], "", r[4]]
        cur.execute("SELECT asset_tag, description FROM assets WHERE asset_pk=%s;", (r[5], ))
        asset = cur.fetchone()
        entry[0] = asset[0]
        entry[1] = asset[1]
        cur.execute("SELECT fcode FROM facilities WHERE facility_pk=%s;", (r[0], ))
        entry[3] = cur.fetchone()[0]
        cur.execute("SELECT fcode FROM facilities WHERE facility_pk=%s;", (r[1], ))
        entry[5] = cur.fetchone()[0]
        add = True
        if len(src_facility) > 0:
            if entry[3] != src_facility:
                add = False
        if len(dest_facility) > 0:
            if entry[5] != dest_facility:
                add = False
        if add:
            data.append(entry)
    session['trans_data'] = data
    return render_template('transit_report.html')

@app.route('/logout')
def logout():
    return render_template("logout.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

