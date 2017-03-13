# vim: background=dark

import psycopg2
import csv
import sys

db = None
cur = None
dbname = None
path = None

# gather user data
def get_user_data():
    global path, cur
    cur.execute("SELECT username, password, role, active FROM users JOIN roles ON role_fk=role_pk;")
    users = [{'username': i[0], 'password': i[1], 'role': i[2], 'active': i[3]} for i in cur.fetchall()] 
    with open(path + '/users.csv', 'a') as csvfile:
        fields = ['username','password','role','active']
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for r in users:
            writer.writerow(r)


# gather facility data
def get_fac_data():
    global path, cur
    cur.execute("SELECT f_code, common_name FROM facilities;")
    facilities = [{'fcode': i[0], 'common_name': i[1]} for i in cur.fetchall()]
    with open(path + '/facilities.csv', 'a') as csvfile:
        fields = ['fcode', 'common_name']
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for r in facilities:
            writer.writerow(r)

# gather asset data
def get_asset_data():
    global path, cur
    cur.execute("SELECT asset_tag, description FROM assets;")
    assets = [{'asset_tag': i[0], 'description': i[1]} for i in cur.fetchall()]
    # get facility and date/time info
    for a in assets:
        cur.execute("""SELECT f_code, intake_dt, expunge_dt FROM assets 
                JOIN asset_at on asset_pk=asset_fk 
                JOIN facilities on facility_fk=facility_pk
                WHERE asset_tag=%s;""", (a['asset_tag'],))
        res = cur.fetchall()
        initial = sorted(res, key=lambda res: res[1], reverse=False)[0]
        a['facility'] = initial[0]
        a['acquired'] = initial[1]
        a['disposed'] = initial[2] if initial[2] is not None else 'NULL'
    with open(path + '/assets.csv', 'a') as csvfile:
        fields = ['asset_tag', 'description', 'facility', 'acquired', 'disposed']
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for r in assets:
            writer.writerow(r)

# gather transfer data
def get_transfer_data():
    global path, cur
    cur.execute("""SELECT asset_tag, requester, request_dt, approver, approve_dt, t.src, t.dest, t.request_id
            FROM transfer_requests t JOIN assets a ON t.asset_fk=a.asset_pk WHERE t.status>=0;""")
    transfers = [{'asset_tag': i[0],
                'request_by': i[1],
                'request_dt': i[2],
                'approve_by': i[3] if i[3] is not None else 'NULL',
                'approve_dt': i[4] if i[4] is not None else 'NULL',
                'source': i[5],
                'destination': i[6],
                'id': i[7]
                } for i in cur.fetchall()]
    # swap facility keys for fcodes
    for t in transfers:
        cur.execute("SELECT f_code FROM facilities WHERE facility_pk=%s;", (t['source'],))
        t['source'] = cur.fetchone()[0]
        cur.execute("SELECT f_code FROM facilities WHERE facility_pk=%s;", (t['destination'],))
        t['destination'] = cur.fetchone()[0]
    # get time info, if any
    for t in transfers:
        cur.execute("SELECT load_dt, unload_dt FROM asset_moving WHERE request_id=%s;", (t['id'],))
        res = cur.fetchone()
        if res is not None:
            t['load_dt'] = res[0] if res[0] is not None else 'NULL'
            t['unload_dt'] = res[1] if res[1] is not None else 'NULL'
        else:
            t['load_dt'] = 'NULL'
            t['unload_dt'] = 'NULL'
        del t['id'] # request_id is not exported
    with open(path + '/transfers.csv', 'a') as csvfile:
        fields = ['asset_tag', 'request_by', 'request_dt', 'approve_by', 'approve_dt', 'source', 'destination', 'load_dt', 'unload_dt']
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for r in transfers:
            writer.writerow(r)

def main():
    global db, cur, dbname, path

    dbname = sys.argv[1]
    path = sys.argv[2]
    db = psycopg2.connect(dbname=sys.argv[1], host="/tmp/", port=5432)
    cur = db.cursor()

    get_user_data()
    get_fac_data()
    get_asset_data()
    get_transfer_data()

if __name__ == "__main__":
    main()




