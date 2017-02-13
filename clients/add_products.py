import sys
import json
import datetime

from urllib.request import Request, urlopen
from urllib.parse import urlencode

def main():
    #Check for missing args
    if len(sys.argv) < 6:
        print("Usage: python3 add_products.py <url> <vendor> <description> <alt_description> <compartments>")
        return

    #prep args blob
    args = {'timstamp': datetime.datetime.utcnow().isoformat()}
    products = {'vendor': sys.argv[2],
            'desciption': sys.argv[3],
            'alt_description': sys.argv[4],
            'compartments': list(sys.argv[5])
    }
    products['compartments'].remove('')
    new_products = []
    new_products.append(products)
    args['new_products'] = new_products

    #Setup data to send
    send_args = {'arguments': json.dumps(args),
            'signature': ''
    }
    data = urlencode(send_args)

    #Make the request
    req = Request(sys.argv[1], data.encode('ascii'), method='POST')
    res = urlopen(req)

    #Parse the response
    resp = json.loads(res.read().decode('ascii'))

    #Print the result
    print("Call to LOST returned: %s" % resp)

if __name__ == '__main__':
    main()
