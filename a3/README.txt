CS456 - Assignment #3 - Readme
Justin Franchetto
20375706

About:
The files router.py, db.py and packetOps.py are written to fulfill the requirements outlined in Assignment #3
An instance of a router can be created with the router.py file, while the other files implement classes necessary for execution, 
such as databases and packets. 

Compilation:
The router was implemented in Python, so there is no need for compilation. However, the makefile is used to generate a bash script
which will be used to execute the routers in the order requested for the assignment. To run the makefile, use the make command. 

Execution:
1) Execute the emulator: ./nse-linux386 localhost 9999
2) Execute the routers: ./router

Parameters:
	Emulator: 
	<routers_host>: the host where the routers are running
	<nse_port>: the port where the emulator is listening

	Router: the parameters of the router are contained in the generated ./router script, but are as follows:

	<router_id>: The id of this router
	<nse_host>: The machine hosting the emulator
	<nse_port>: The port to communicated with the emulator on
	<router_port>: The port on this router used for communicating

Machines:
These programs were tested across three different machines in the student environment:
	1) Emulator was run on ubuntu1204-006
	2)./router was run on ubuntu1204-004, where all five routers are running. 

