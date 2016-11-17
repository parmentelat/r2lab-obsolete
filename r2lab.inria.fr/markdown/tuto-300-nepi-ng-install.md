title: Installing nepi-ng
tab: tutorial
float_menu_template: r2lab/float-menu-tutorials.html
---

For running experiments right from your own laptop, we provide a set of tools, that we collectively refer to as `nepi-ng`. This page gives you detailed instructions for installing these.

## Terminal-based

All the tools that we will write will run in a terminal, we assume you are familiar with dealing with such interfaces.

## Requires python-3.5

`nepi-ng` is a set of python libraries; these use [the `asyncio` library](https://docs.python.org/3/library/asyncio.html), 
and as such require python-3.5 (as we use the latest `async def` and `await` syntax, that won't work under python-3.4).
Please refer to the python documentation for installing that version of python on your laptop.
You can check that this requirement is fulfilled by running

    $ python3 --version
    Python 3.5.1

## Installing `asynciojobs` and `apssh`


You need to install these libraries, the recommended way is through
`pip3` like this (if you're not using `virtualenv` or ` anaconda`, you
might need to run these commands under `sudo`)

    pip3 install asynciojobs apssh

Note that for upgrading to the latest release published on `pypi.org`, you need to run

    pip3 install --upgrade asynciojobs apssh

You can check the installed versions like this

    $ python3 -c 'from asynciojobs import version; print(version.version)'
    0.2.3
    $ python3 -c 'from apssh import version; print(version.version)'
    0.2.17

## Note on ssh and ssh-agent

`nepi-ng` **does not require** a native ssh client to be installed on
your laptop, as it uses the great `asyncssh` library instead. However,
it is recommended to have one installed, if only for running an ssh
agent, as using ssh repeatedly is almost impossible without an
ssh-agent.

You will see that in all the code of these tutorials, there is no
option to specify an alternate key. This is because all the examples
in this tutorial use **the set of keys known to your ssh agent**.

You can inspect and manage this set of keys using the `ssh-add`
command - at least on unix-based systems.

    ~/.ssh $ ssh-add -l
    1024 SHA256:KNm0U4SgFV9bY957hJAIRR68n5AZHQ6e1gbiXrGHuOA onelab.private (RSA)
    ~/.ssh $ ssh-add onelab.private
    Enter passphrase for onelab.private:
    Identity added: onelab.private (onelab.private)
    ~/.ssh $ ssh-add -l
    1024 SHA256:KNm0U4SgFV9bY957hJAIRR68n5AZHQ6e1gbiXrGHuOA /Users/parmentelat/.ssh/id_rsa (RSA)
    2048 SHA256:WvCdpP+FHBTnkwbkqYl43GVgwEK2iYdwRaNm+fCc+Xg onelab.private (RSA)
