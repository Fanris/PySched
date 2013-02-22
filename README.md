# PySched  

PySched - A python network Scheduler

## Installation ##

### PySchedServer:  ###
	1. Create a System-User named 'pysched'  
	2. Create a public/private key pair for this user  
		- The private key is distributed to all Users / Workstations
		which are authorized to connect to the server.  
		- The public key must be stored within the .ssh/authorized_keys file of the
		created user.  
		- Also ssh authorization with public keys must be enabled on the server  
	3. Install the PySched-Software
	5. Create a working directory for the PySchedServer  
	6. Start the server with the path to the working directory as first parameter  

### PySchedClient (Workstation):  ###
	1. Create a System-User named 'pysched'  
	2. Copy the PySchedServer files to the new users home  
	3. Install the PySched-Software
	4. Copy the private key of the server to the PySchedClient working folder  
	5. Rename it to 'pysched.rsa'  
	6. Create a working directory for the PySchedClient  
	7. Start the Client with the path to the working directory as first parameter  

### User-Interface:  ###
	1. Copy the PySched user interface anywhere on your machine  
	2. Install the PySched-UI
	3. Get the servers private key from your administrator.  
	4. Start the user interface with the following parameters  
		- --key=Path/To/PrivateKey  
		- --user=Your username (optional)  
		- ui (to start the "graphical" UI)  
