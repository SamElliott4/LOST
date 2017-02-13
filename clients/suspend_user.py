import sys
import json
import datetime

from urllib.request import Request, urlopen
from urllib.parse import urlencode

def main():
    if len(sys.argv) < 3:
        print("Usage python3 suspend_user.py <url> <username>")
        return

    args = {'timestamp': datetime.datetime.utcnow().isoformat(),
            'username': sys.argv[2]
    }

    print("Suspending user: %s" % args['username'])

    send_args = {'arguments': json.dumps(args),
                 'signature': ''
    }
    data = urlencode(send_args)

    req = Request(sys.argv[1], data.encode('ascii'), method='POST')
    res = urlopen(req)

    resp = json.loads(res.read().decode('ascii'))

    print("Call to lost returned: %s" % resp['result'])

if __name__ == '__main__':
    main()
