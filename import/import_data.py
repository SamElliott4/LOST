# vim: background=dark

import csv
import sys
import psycopg2

dbname = sys.argv[1]
path = sys.argv[2]

db = psycopg2.connect(dbname=dbname, host='/tmp/', port='5432')
cur = db.cursor()

def main():
    global db, cur, path
    # import users and facilties first, no internal dependencies 
    # users
    with open(path + '/users.csv', 'r') as csvfile:
        users = []
        reader = csv.DictReader(csvfile)
        for r in reader:
            users.append([r['username'], r['password'], r['role'], r['active']])
        for u in users:
            cur.execute("SELECT role_pk FROM roles WHERE role ILIKE %s;", (u[2],))
            role_key = cur.fetchone()[0]
            cur.execute("""INSERT INTO users (user_id, username, password, role_fk, active)
                    VALUES (%s, %s, %s, %s, %s);""", (u[0].lower(), u[0], u[1], role_key, u[3]))
            db.commit()
    
    
    # facilities
    with open(path + '/facilities.csv', 'r') as csvfile:
        facilities = []
        reader = csv.DictReader(csvfile)
        for r in reader:
            facilities.append([r['fcode'], r['common_name']])
        for f in facilities:
            # try block, log failed entries
            cur.execute("INSERT INTO facilities (f_code, common_name) VALUES (%s, %s);", (f[0], f[1]))
            db.commit()
    
    # import assets
    with open(path + '/assets.csv', 'r') as csvfile:
        assets = []
        reader = csv.DictReader(csvfile)
        for r in reader:
            assets.append([r['asset_tag'], r['description'], r['facility'], r['acquired'], r['disposed']])
        for a in assets:
            # new asset in asset table
            cur.execute("INSERT INTO assets (asset_tag, description) VALUES (%s, %s);", (a[0], a[1]))
            db.commit()
            # new entry in asset_at table
            cur.execute("SELECT asset_pk FROM assets WHERE asset_tag=%s;", (a[0],))
            asset_key = cur.fetchone()[0]
            cur.execute("SELECT facility_pk FROM facilities WHERE f_code=%s;", (a[2],))
            fac_key = cur.fetchone()[0]
            cur.execute("INSERT INTO asset_at (asset_fk, facility_fk, intake_dt, expunge_dt) VALUES (%s, %s, %s, %s);",
                    (asset_key, fac_key, a[3], a[4] if a[4] != 'NULL' else None))
            # asset status is unknown until after transfer import
            db.commit()
    
    # import tranfers
    with open(path + '/transfers.csv', 'r') as csvfile:
        transfers = []
        reader = csv.DictReader(csvfile)
        for r in reader:
            cur.execute("SELECT * FROM transfer_requests;")
            req_num = len(cur.fetchall())+1
            cur.execute("SELECT asset_pk FROM assets WHERE asset_tag=%s;", (r['asset_tag'],))
            asset_key = cur.fetchone()[0]
            cur.execute("SELECT facility_pk FROM facilities WHERE f_code=%s;", (r['source'],))
            src_key = cur.fetchone()[0]
            cur.execute("SELECT facility_pk FROM facilities WHERE f_code=%s;", (r['destination'],))
            dest_key = cur.fetchone()[0]
            req_id = r['source'] + str(req_num)
            if r['approve_by'] == 'NULL':
                t_status = 0
                approve_by = None
                approve_dt = None
            else:
                t_status = 1      
                approve_by = r['approve_by']
                approve_dt = r['approve_dt']
            cur.execute("""INSERT INTO transfer_requests (request_id, asset_fk, requester, request_dt, src, dest, approver, approve_dt, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                    (req_id, asset_key, r['request_by'], r['request_dt'], src_key, dest_key, approve_by, approve_dt, t_status))
            if t_status == 1:
                load_dt = r['load_dt']
                if load_dt == 'NULL':
                    load_dt = None
                unload_dt = r['unload_dt']
                if unload_dt == 'NULL':
                    unload_dt = None
                cur.execute("""INSERT INTO asset_moving (request_id, asset_fk, src, dest, load_dt, unload_dt) 
                        VALUES (%s, %s, %s, %s, %s, %s);""", (req_id, asset_key, src_key, dest_key, load_dt, unload_dt))
            db.commit()
    
    # fill out asset_at based on asset_moving table
    cur.execute("SELECT asset_pk FROM assets;")
    assets = cur.fetchall()
    for a in assets:
        cur.execute("SELECT dest, load_dt, unload_dt FROM asset_moving WHERE asset_fk=%s;", (a[0],))
        res = cur.fetchall()
        rem = []
        for i in res:
            if i[1] == None:
                rem.append(i)
        for i in rem:
            res.remove(i)
        asc_res = sorted(res, key=lambda res: res[1], reverse=False)
        for b in asc_res:
            current_loc = latest_asset_loc(a[0])
            cur.execute("UPDATE asset_at SET expunge_dt=%s WHERE intake_dt=%s;", (b[1], current_loc[2]))
            a_status = 2
            if b[2]:
                cur.execute("INSERT INTO asset_at (asset_fk, facility_fk, intake_dt) VALUES (%s, %s, %s);", (a[0], b[0], b[2]))
                a_status = 1
            # update asset_status
            cur.execute("UPDATE assets SET status=%s WHERE asset_pk=%s;", (a_status, a[0]))
            db.commit()


    #check for disposed assets:
    cur.execute("SELECT asset_pk FROM assets;")
    assets = cur.fetchall()
    for a in assets:
        latest = latest_asset_loc(a[0])
        if latest[3]:
            cur.execute("SELECT * FROM asset_at a JOIN asset_moving m ON expunge_dt=load_dt WHERE a.asset_fk=%s AND a.expunge_dt=%s;", (a[0], latest[3]))
            if len(cur.fetchall()) == 0:
                cur.execute("UPDATE assets SET status=0 WHERE asset_pk=%s;", (a[0],))
        else:
            cur.execute("UPDATE assets SET status=1 WHERE asset_pk=%s;", (a[0],))
        db.commit()



def latest_asset_loc(asset_key):
    cur.execute("SELECT asset_fk, facility_fk, intake_dt, expunge_dt FROM asset_at WHERE asset_fk=%s;", (asset_key,))
    res = cur.fetchall()
    return sorted(res, key=lambda res: res[2], reverse=True)[0]

if __name__ == "__main__":
    main()



