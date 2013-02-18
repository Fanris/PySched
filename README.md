PySched
===

PySched - A python network Scheduler

1. Installation
---

1.1 PySchedServer:
	1. Create a System-User named 'pysched'
	2. Create a public/private key pair for this user
		- The private key is distributed to all Users / Workstations
		which are authorized to connect to the server.
		- The public key must be stored within the .ssh/authorized_keys file of the
		created user.
		- Also ssh authorization with public keys must be enabled on the server
	3. Copy the PySchedServer files to the new users home
	4. Install the required python packages
		- paramiko
		- python-twisted
		- sqlalchemy
	5. Create a working directory for the PySchedServer
	6. Start the server with the path to the working directory as first parameter

1.2 PySchedClient (Workstation):
	1. Create a System-User named 'pysched'
	3. Copy the PySchedServer files to the new users home
	4. Install the required python packages
		- paramiko
		- python-twisted
		- sqlalchemy
	5. Copy the private key of the server to the PySchedClient working folder
	6. Rename it to 'pysched.rsa'
	7. Create a working directory for the PySchedClient
	8. Start the Client with the path to the working directory as first parameter

1.3 User-Interface:
	1. Copy the PySched user interface anywhere on your machine
	2. Install the required python packages
		- paramiko
	3. Get the servers private key from your administrator.
	4. Start the user interface with the following parameters
		- --key=Path/To/PrivateKey
		- --user=Your username (optional)
		- ui (to start the "graphical" UI)
