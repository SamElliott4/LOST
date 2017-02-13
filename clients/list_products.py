import sys
import json
import datetime

from urllib.request import Request, urlopen
from urllib.parse import urlencode

def main():
    #Check for missing args
    if len(sys.argv) < 5:
        print("Usage: python3 list_products <url> <vendor> <description> <compartments>")
        return

    #prep args blob
    args = {'timestamp': datetime.datetime.utcnow().isoformat(),
            'vendor': sys.argv[2],
            'description': sys.argv[3],
            'compartments' = list(sys.argv[4].split(',')
    }
    #handle empty compartments arg
    args['compartments'].remove('')

    #Setup data to send
    send_args = {'arguments': json.dump(args),
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
