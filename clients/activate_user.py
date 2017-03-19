# vim: background=dark

import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode

def main():
    # Check args
    if len(sys.argv) < 5:
        print("Usage: python3 activate_user.py <host url> <username> <password> <role>")
        return
    
    # parse role
    if sys.argv[4] == 'facofc':
        role = 'Facilities Officer'
    elif sys.argv[4] == 'logofc':
        role = 'Logistics Officer'
    else:
        print("Unknown role. Options are 'logofc' for Logistics Officer or 'facofc' for Facilities Officer")
        return

    # encode data to be passed
    args = {'username': sys.argv[2], 'password': sys.argv[3], 'role': role}
    data = urlencode(args)

    # Make the request and pass it to the web service
    req = Request(sys.argv[1] + 'create_user', data.encode('ascii'), method='POST')
    res = urlopen(req)

    # Print the result to stdout
    print(res.read().decode('ascii'))

if __name__ == '__main__':
    main()

