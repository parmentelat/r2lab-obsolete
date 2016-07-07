#Problem
We have nodes #4 and #18 that apparently works fine in all basic functions (load, on, off, etc),
except by the remote **reset** command.
It means that when we sent the reset command thought the network the command is not executed at the node at all.

#Tests
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

#Conclusion
The physically reset, when applied, always worked fine in the node.
The remote ON/OFF command always worked fine.
Seems the Arduino card after a while (~ 3min) do not answer anymore to the remote RESET command.
