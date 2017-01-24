import csv
import psycopg2
import datetime
import sys
from lost_input import *

filePath = "osnap_legacy/"
fileList = [
    'acquisitions', 
    'convoy', 
    'DC_inventory', 
    'HQ_inventory', 
    'MB005_inventory', 
    'NC_inventory', 
    'product_list', 
    'security_compartments',
    'security_levels',
    'SPNV_inventory',
    'transit',
    'vendors'
]

#Generic function to extract the data from the csv files
def extractContents(filename):
    #returns a list of dicts
    with open(filePath + filename, 'rt') as file:
        reader = csv.reader(file)
        output = []
        rowNum = 0
        for row in reader:
            if rowNum == 0:
                header = row
            else:
                colNum = 0
                newDict = {}
                for col in row:
                    newDict[header[colNum]] = col
                    colNum += 1
                output.append(newDict)
            rowNum += 1
    return output
#reformat date/time entries used in legacy data
def convertTimestamp(str):
    dt = str.split(" ")
    time = ["0", "0", "0"]
    date = dt[0].split("/")
    if len(date) == 1:
        date = dt[0].split("-")
        monthNum = {'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4, 'May' : 5, 'Jun' : 6, 'Jul' : 7, 'Aug' : 8, 'Sep' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12}
        if len(date) == 3:
            day = date[0]
            month = monthNum[date[1]]
            year = date[2]
            date[0] = month
            date[1] = day
            date[2] = year
        if len(date) == 2:
            month = monthNum[date[0]]
            day = date[1]
            year = "2016"
            if month == 1 and day < 16:
                year = "2017"
            date[0] = month
            date[1] = day
            date.append(year)
    if len(date[2]) == 2:
        date[2] = "20" + date[2]
    if len(dt) == 2:
        time2 = dt[1].split(":")
        for i in range(0, len(time2)):
            time[i] = time2[i] #To avoid possible index error in next line
        newDT = datetime.datetime(year = int(date[2]), month = int(date[0]), day = int(date[1]), hour = int(time[0]), minute = int(time[1]), second = int(time[2]))
        return newDT
    newDT = datetime.datetime(year = int(date[2]), month = int(date[0]), day = int(date[1]))
    return newDT

def main():
    #Import all data, preserving file name as variable name	
    data = {key: extractContents(key + '.csv') for key in fileList}
    #Connect to database
    connectDB(sys.argv[1], sys.argv[2])

    #Migrate data starting with items that have no internal dependencies (no foreign keys required)
    #levels
    for d in data['security_levels']:
        newLevel(d['level'], d['description'])

    #compartments
    for d in data['security_compartments']:
        newCompartment(d['compartment_tag'], d['compartment_desc'])

    #products
    for d in data['product_list']:
        #fix a typo
        if d['vendor'] == 'big n large':
            d['vendor'] = 'buy n large'
        newProduct(d['vendor'], d['name'], d['description'])
        #new tag(s)
        if len(d['compartments']) > 0:
            tags = d['compartments'].split(', ')
            for tag in tags:
                sec = tag.split(':')
                comp_fk = getKey('compartments', 'abbrv', sec[0])
                level_fk = getKey('levels', 'abbrv', sec[1])
                product_fk = getKey('products', 'description', d['name'])
                newTag(level_fk, comp_fk, None, product_fk, None)
		
    #facilities
        #Since there is no list of facilities and corresponding identifying codes
        #I am using every mentioned facility in the legacy data, and introducing 
        #fcodes in a consistent manner. Doing this part procedurally would 
        #be unrealistic.
        #Data taken from 'transit.csv'
        #fcodes derived from 'transport request' field and _inventory files
    facilities = {
        'MB 005' : 'MB',
        'Site 300' : 'ST',
        'Groom Lake' : 'GL',
        'Los Alamos, NM' : 'LA',
        'Headquarters' : 'HQ',
        'National City' : 'NC',
        'Sparks, NV' : 'SP',
        'Washington, D.C.' : 'DC'
    }
    for key in facilities:
        newFacility(facilities[key], key, None)

    #assets
    for d in data['DC_inventory']:
        newAsset(None, d['asset tag'], d['product'], None)
        # asset_at entry for DC inventory
        asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
        facility_fk = getKey('facilities', 'fcode', 'DC')
        if len(d['intake date']) > 0:
            arrive_dt = convertTimestamp(d['intake date'])
        else:
            arrive_dt = None
        if len(d['expunged date']) > 0:
            depart_dt = convertTimestamp(d['expunged date'])
        else:
            depart_dt = None
        newAssetAt(asset_fk, facility_fk, arrive_dt, depart_dt)
        #new tag(s)
        if len(d['compartments']) > 0:
            tags = d['compartments'].split(', ')
            for tag in tags:
                sec = tag.split(':')
                comp_fk = getKey('compartments', 'abbrv', sec[0])
                level_fk = getKey('levels', 'abbrv', sec[1])
                asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
                newTag(level_fk, comp_fk, None, None, asset_fk)
    for d in data['HQ_inventory']:
        newAsset(None, d['asset tag'], d['product'], None)
        # asset_at for HQ inventory
        asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
        facility_fk = getKey('facilities', 'fcode', 'HQ')
        if len(d['intake date']) > 0:
            arrive_dt = convertTimestamp(d['intake date'])
        else:
            arrive_dt = None
        if len(d['expunged date']) > 0:
            depart_dt = convertTimestamp(d['expunged date'])
        else:
            depart_dt = None
        newAssetAt(asset_fk, facility_fk, arrive_dt, depart_dt)
        #new tag(s)
        if len(d['compartments']) > 0:
            tags = d['compartments'].split(', ')
            for tag in tags:
                sec = tag.split(':')
                comp_fk = getKey('compartments', 'abbrv', sec[0])
                level_fk = getKey('levels', 'abbrv', sec[1])
                asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
                newTag(level_fk, comp_fk, None, None, asset_fk)
    for d in data['MB005_inventory']:
        newAsset(None, d['asset tag'], d['product'], None)
        #asset_at entry for MB
        asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
        facility_fk = getKey('facilities', 'fcode', 'MB')
        if len(d['intake date']) > 0:
            arrive_dt = convertTimestamp(d['intake date'])
        else:
            arrive_dt = None
        if len(d['expunged date']) > 0:
            depart_dt = convertTimestamp(d['expunged date'])
        else:
            depart_dt = None
        newAssetAt(asset_fk, facility_fk, arrive_dt, depart_dt)
        #new tag(s)
        if len(d['compartments']) > 0:
            tags = d['compartments'].split(', ')
            for tag in tags:
                sec = tag.split(':')
                comp_fk = getKey('compartments', 'abbrv', sec[0])
                level_fk = getKey('levels', 'abbrv', sec[1])
                asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
                newTag(level_fk, comp_fk, None, None, asset_fk)
    for d in data['NC_inventory']:
        newAsset(None, d['asset tag'], d['product'], None)
        #asset_at entry for NC inventory
        asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
        facility_fk = getKey('facilities', 'fcode', 'NC')
        if len(d['intake date']) > 0:
            arrive_dt = convertTimestamp(d['intake date'])
        else:
            arrive_dt = None
        if len(d['expunged date']) > 0:
            depart_dt = convertTimestamp(d['expunged date'])
        else:
            depart_dt = None
        newAssetAt(asset_fk, facility_fk, arrive_dt, depart_dt)
        #new tag(s)
        if len(d['compartments']) > 0:
            tags = d['compartments'].split(', ')
            for tag in tags:
                sec = tag.split(':')
                comp_fk = getKey('compartments', 'abbrv', sec[0])
                level_fk = getKey('levels', 'abbrv', sec[1])
                asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
                newTag(level_fk, comp_fk, None, None, asset_fk)
    for d in data['SPNV_inventory']:
        newAsset(None, d['asset tag'], d['product'], None)
        #asset_at entry for SP
        asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
        facility_fk = getKey('facilities', 'fcode', 'SP')
        if len(d['intake date']) > 0:
            arrive_dt = convertTimestamp(d['intake date'])
        else:
            arrive_dt = None
        if len(d['expunged date']) > 0:
            depart_dt = convertTimestamp(d['expunged date'])
        else:
            depart_dt = None
        newAssetAt(asset_fk, facility_fk, arrive_dt, depart_dt)
        #new tag(s)
        if len(d['compartments']) > 0:
            tags = d['compartments'].split(', ')
            for tag in tags:
                sec = tag.split(':')
                comp_fk = getKey('compartments', 'abbrv', sec[0].lower())
                level_fk = getKey('levels', 'abbrv', sec[1].lower())
                asset_fk = getKey('assets', 'asset_tag', d['asset tag']) 
                newTag(level_fk, comp_fk, None, None, asset_fk)

    #convoys
    for d in data['transit']:
        #find more precise timestamp in 'convoy.csv' by request #
        dept=None
        arrv=None
        for d2 in data['convoy']:
            if d['transport request #'] == d2['transport request #']:
                dept = convertTimestamp(d2['depart time'])
                arrv = convertTimestamp(d2['arrive time'])
        #fetch src, dest from facility table by name
        if d['src facility'] == 'Los Alamous, NM' or d['src facility'] == 'Las Alamos, NM':
            d['src facility'] = 'Los Alamos, NM' #one-off typo fix
        src = getKey('facilities', 'common_name', d['src facility'])
        dest = getKey('facilities', 'common_name', d['dst facility'])
        newConvoy(d['transport request #'], src, dest, dept, arrv)
		
        #migrate asset_on data now that convoy_fk is available
        transitAssets = d['asset tag'].split(', ')
        for a in transitAssets:
            #asset_fk by asset tag from assets table
            asset_fk = getKey('assets', 'asset_tag', a)
            #convoy_fk by 'request' from convoys table
            convoy_fk = getKey('convoys', 'request', d['transport request #'])
            newAssetOn(asset_fk, convoy_fk, dept, arrv)

    #vehicle assets
    for d in data['convoy']:
        vehicles = d['assigned vehicles'].split(', ')
        for v in vehicles:
            # entry to assets
            newAsset(None, v, "transport vehicle", None)
            # entry to vehicles (needed asset_fk)
            asset_fk = getKey('assets', 'asset_tag', v)
            newVehicle(asset_fk)
            # new used_by entry
            vehicle_fk = getKey('vehicles', 'asset_fk', str(asset_fk))
            convoy_fk = getKey('convoys', 'request', d['transport request #'])
            newUsedBy(vehicle_fk, convoy_fk)


if __name__ == "__main__":
	main()
