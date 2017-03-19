This directory contains clients that govern user creation and handling for the LOST system.

clients:
activate_user.py - Usage: python3 activate_user.py <host url> <username> <password> <role>
	example: python3 activate_user.py http://127.0.0.1:8080/ Rick giveyouup logofc
    Functionality: 
	If given a non-existent username, a new user will be created with the given name, password, and role 
	  (logofc = Logistics Officer, facofc = Facilities Officer)
	If given an existing username, the users password will be updated with the new password, and the user will be made active
	After initial creation, a user cannot be assigned a different role, regardless of what role is passed

revoke_user.py - Usage: python3 revoke_user.py <host url> <username>
	example: python3 revoke_user.py http://127.0.0.1/ Rick
    Funtionality:
	If given a non-existent username, nothing happens
	If given an existing username, that user is made inactive. The user can be reactivated with activate_user.py
