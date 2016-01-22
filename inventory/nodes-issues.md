# Issues nodes at R2lab
The present document aims to document all know/common bugs and issues related to the nodes located at R2lab platform (faraday).

## Errors/Issues

###EI.001 
The supposed load charge occurs normally until the reboot starts. The node answers for the telnet and the ssh, however does not start. This happens only for our Ubuntu **10.14** (Thierry: I assume you mean **14.10** here of course)

#### How to deal with
- We are avoiding at the moment load automaticlly this version.

#### Notes
* In the old times we had issues with ubuntu startup; essentially the system was asking the user - expected to be sitting in front of the screen - if she wants to perform a filesystem check; I cannot remember how long this would wait for an answer. It would make sense to check if that can be the case here too. It could be related to the disk partition layout in the image in question.
	
### EI.002
The node does not answer for the command "off" or "curl 192.168.1.xx/off" in faraday terminal.

#### How to deal with
* A double command (off [enter]; off [enter]) will surcharge the CM and the node will process the off. The answer in terminal could be "CM card busy".
* A physical reset in the CM card is mandatory. Disconnect the power cable, wait for a while, and connect again. MUST reconfigure the BIOS. See google docs for the BIOS setup.
* One simpler way to achieve this in the chamber is to use the wall power control panel to turn all the nodes on and off in a single move.


###EI.003
The node does not receive - or at least react - upon the "on" message.
The blue light is switch on, however, the trigger to start the node never happens when I send the command to do it. 

#### How to deal with
- No solution, yet...


###EI.004
The node takes to much time to load and fails to start the O.S. 

#### How to deal with
- The BIOS configuration for some reason was lost. Mainly the *Quick Setup* option. See google docs to have the BIOS setup.