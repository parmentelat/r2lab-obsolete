#Problem detected
We have two nodes (#4 and #18) that do not execute the remote command RESET after a while when turned on.
It means that when we sent the RESET command thought the network the command is not executed at all.

#How it happens
After a while turned on, the node do not responds anymore the remote RESET command.

#How reproduce
Considering the node in OFF state, with no energy cable plugged for at least 5 minutes.
Plug the energy cable, start the node using ON remote command. Once did, the remote command RESET will work
properly for ~ 3min. After this period, the node do not respond anymore to the RESET remote command.
To get the remote RESET command working again, it is obligatory remove the energy cable and leave the node unplugged for ~5min. or more.

#Tests made
In order reproduced and detect the problem we removed both nodes from the anechoic chamber and placed them at our lab.
Then, we setup both nodes using only:
- Energy cable
- On/Off/Reset wired network cable

##1 - physical reset
- A remote ON command was sent. (PASS)
- RESET physically many times. (PASS)
- A remote OFF command was sent. (PASS)

##2 - starting node after no cables plugged
- All cables unplugged.
- All cables plugged, after ~5min.
- A remote ON command was sent. (PASS)
- A remote RESET command was sent after 10sec, 20sec, 30sec and 1min. (PASS)
- A remote RESET command was sent after 3min. (FAIL)
- A remote OFF command was sent. (PASS)

  ##2.1 - after a while from the last OFF command in test #2
  - A remote ON command was sent. (PASS)
  - A remote RESET command was sent after 10sec, 20sec, 30sec and 1min. (FAIL)
  - A remote RESET command was sent after 3min. (FAIL)
  - A remote OFF command was sent. (PASS)

##3 - starting node after removing Energy cable
- Energy cable unplugged (On/Off/Reset cable plugged).
- Energy cable plugged, after ~5min.
- A remote ON command was sent. (PASS)
- A remote RESET command was sent after 10sec, 20sec, 30sec and 1min. (PASS)
- A remote RESET command was sent after 3min. (FAIL)
- A remote OFF command was sent. (PASS)

  #3.1 - after a while from the last OFF command in test #3
  - A remote ON command was sent. (PASS)
  - A remote RESET command was sent after 10sec, 20sec, 30sec and 1min. (FAIL)
  - A remote RESET command was sent after 3min. (FAIL)
  - A remote OFF command was sent. (PASS)

  ##3.2 - physically reset
  - A remote ON command was sent. (PASS)
  - RESET physically many times. (PASS)
  - A remote OFF command was sent. (PASS)

##4 - starting node after removing On/Off/Reset cable
- On/Off/Reset cable unplugged (energy cable plugged), after ~5min.
- On/Off/Reset cable plugged.
- A remote ON command was sent. (PASS)
- A remote RESET command was sent after 10sec, 20sec, 30sec and 1min. (FAIL)
- A remote RESET command was sent after 3min. (FAIL)
- A remote OFF command was sent. (PASS)

  ##4.1 - trying again after a while from the last OFF command in test #4
  - A remote ON command was sent. (PASS)
  - A remote RESET command was sent after 10sec, 20sec, 30sec and 1min. (FAIL)
  - A remote RESET command was sent after 3min. (FAIL)
  - A remote OFF command was sent. (PASS)

  ##4.2 - physically reset
  - A remote ON command was sent. (PASS)
  - RESET physically many times. (PASS)
  - A remote OFF command was sent. (PASS)

#Update in hardware
Two actions were made concerning the hardware.
- We replaced partially the CMC card.
  CMC card is composed by an Arduino board + another circuit affixed on top. We were not able to replace the second component because we don't have a backup of this card for now.
- Burned again the firmware

No different result appeared as answer of these changes. The node behavior was exactly the same as described before.

#Some infos about it
Turn the node off without unplugged the energy cable do not make any effect in remote RESET command.
In any phase of the tests, all others basic commands worked properly (On, Off, Load) on the node.
More than once in the tests, at some point, the node was switched off and a physical RESET button was placed. In all these cases the RESET worked perfectly. Even when the energy cable remained plugged.

#Conclusion
The physically reset, when applied, always worked fine in the node.
The remote ON/OFF command always worked fine.
Seems the Arduino card after a while (~ 3min) do not answer anymore to the remote RESET command.
