import sys
import json
import datetime

from urllib.request import Request, urlopen
from urllib.parse import urlencode

def main():
    #Check for missing args
    if len(sys.argv) < 2:
        print("Usage: python3 lost_key.py <url>")
        return

    #prep args blob
    

    #Setup data to send
    send_args = {'arguments': '',
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
