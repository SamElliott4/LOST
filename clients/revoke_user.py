# vim: background=dark

import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode

def main():
    # Check args
    if len(sys.argv)<3:
        print("Usage: python3 revoke_user.py <host url> <username>")
        return

    # Encode data
    args = {'username': sys.argv[2]}
    data = urlencode(args)

    # Make the request to the webservice
    req = Request(sys.argv[1] + 'revoke_user', data.encode('ascii'), method='POST')
    res = urlopen(req)

    # Print the response to stdout
    print(res.read().decode('ascii'))

if __name__ == '__main__':
    main()
