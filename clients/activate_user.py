import json
import sys
import datetime

from urllib.request import Request, urlopen
from urllib.parse import urlencode

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 filename <url> <username>")
        return

    args = {}
    args['timestamp'] = datetime.datetime.utcnow().isoformat()
    args['username'] = sys.argv[2]

    print("Activating user: %s" %args['username'])


    send_args = {}
    send_args['arguments'] = json.dumps(args)
    send_args['signature'] = ''
    data = urlencode(send_args)

    req = Request(sys.argv[1], data.encode('ascii'),method='POST')
    res = urlopen(req)

    response = json.loads(res.read().decode('ascii'))

    print(response)

if __name__ == "__main__":
    main()
