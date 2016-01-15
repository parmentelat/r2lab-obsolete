# Issues nodes at R2lab
The related document aims document all know/common bugs and issues related to the nodes located at R2lab platform (faraday).

### Errors/Issues
####EI.001 
The supposed load charge occurs normally until the reboot start. The node answer for the telnet and the ssh, however do not start. This happens only for our Ubuntu 10.14.
##### How deal with
- We are avoiding at the moment load automaticlly this version. 
	
####EI.002
The node do not answer for the command "off" or "curl 192.168.1.xx/off" in faraday terminal.
##### How deal with
- A double command (off [enter]; off [enter]) will surcharge the CM and the node will process the off. The answer in terminal could be "CM card busy".
- A physical reset in the CM card is mandatory. Disconnect the power cable, wait for a while, and connect again. MUST reconfigure the BIOS. See google docs the setup.

####EI.003
The node don't receive the "on" message. Well, maybe receive and do not process.
The blue light is switch on, however, the trigger to start the node never happens when I send the command to do it. 
##### How deal with
- No solution, yet...

####EI.004
The node takes to much time to load and fails to start the O.S. 
##### How deal with
- The BIOS configuration for some reason was lost. Mainly the option quick setup. See google docs to have the BIOS setup.