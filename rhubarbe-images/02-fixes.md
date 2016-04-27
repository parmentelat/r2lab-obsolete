# known issues

## `fixdata`

##### Ubuntu and `/etc/network/interfaces` 

I have seen images where the files reads

```
# the data network interface - optional
auto data
#iface data inet dhcp
```

instead of the expected

```
# the data network interface - optional
#auto data
iface data inet dhcp
```

##### Fixes

| image                   | status   | fix-date |
|-------------------------|----------|----------|
| ubuntu-14.04            | DONE     | 16/04/27 |
| ubuntu-16.04            | DONE     | 16/04/27 |
| ubuntu-14.04-k3.19-lowl | DONE     | 16/04/27 |
| ubuntu-12.04            | ???      |          |
| ubuntu-14.10            | ???      |          |
| ubuntu-15.04            | ???      |          |
| ubuntu-15.10            | INSP.      |          |