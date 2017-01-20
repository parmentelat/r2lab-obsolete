title: Installing nepi-ng
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#INSTALL">INSTALL</a> </li>
  <li> <a href="#SSHAGENT">SSH AGENT</a></li>

  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ INSTALL ------------>
<div id="INSTALL" class="tab-pane fade in active" markdown="1">

# What is `nepi-ng` ?
The commands that we have seen in the previous tutorial are useful for
making quick changes on the testbed.

However once you are set up, it is much more convenient to control
experiments right from your own laptop, and to this end we provide a
set of tools that we collectively refer to as `nepi-ng`.

### `nepi-ng` = `asynciojobs` + `apssh`

`nepi-ng` is simply made of 2 python libraries. This page gives you
detailed instructions for installing them. You will also find a more
complete documentation on these 2 tools below :

* [the `asynciojobs` documentation](http://nepi-ng.inria.fr/asynciojobs)
  including [its API reference](http://nepi-ng.inria.fr/asynciojobs/API.html)
* [the `apssh` documentation](http://nepi-ng.inria.fr/apssh)
  including [its API reference](http://nepi-ng.inria.fr/apssh/API.html)

### Terminal-based

All the tools that we will write will run in a terminal, we assume you
are familiar with dealing with such interfaces.

***

# Requires python-3.5

`nepi-ng` is a set of python libraries; these use [the `asyncio`
library](https://docs.python.org/3/library/asyncio.html), and as such
require python-3.5 (as we use the latest `async def` and `await`
syntax, that won't work under python-3.4).  Please refer to the python
documentation for installing that version of python on your laptop.
You can check that this requirement is fulfilled by running

    $ python3 --version
    Python 3.5.1

***

# Installing requirement `asyncssh`

`apssh` has a core dependency to a third-party library named
[`asyncssh`](https://github.com/ronf/asyncssh); this in turn requires
binary extensions, so here's our recommendation to install this
library. Use `sudo` for running `pip3` unless you are working in a
`virtualenv` or similar.

### Ubuntu

Tested on Ubuntu-16

    sudo apt-get install libssl-dev
    [sudo] pip3 install asyncssh


### Fedora

Here's a - possibly non-exhaustive - list of dependencies that help building
`asyncssh`

Tested on fedora-23

    sudo dnf install redhat-rpm-config python3-cffi python3-devel openssl-devel
    [sudo] pip3 install asyncssh

### MacOS

It is harder to describe the list of dependencies on the MAC, let us
know if you run into any trouble when running simply the following

     [sudo] pip3 install asyncssh

***

# Installing `asynciojobs` and `apssh`

You need to install these libraries, the recommended way is through
`pip3` like this - if you're not using `virtualenv` or ` anaconda`, you
might need to run these commands under `sudo`&nbsp;:

    [sudo] pip3 install asynciojobs
    [sudo] pip3 install apssh

You can check the installed versions like this

    $ python3 -c 'from asynciojobs import version; print(version.version)'
    0.4.3
    $ python3 -c 'from apssh import version; print(version.version)'
    0.4.6

Note that if you need to upgrade in the future, you will need to run

    [sudo] pip3 install --upgrade asynciojobs apssh

and that will bring you the latest release published on `pypi.org`.

</div>

<!------------ SSHAGENT ------------>
<div id="SSHAGENT" class="tab-pane fade" markdown="1">

### ssh and ssh-agent

`nepi-ng` **does not require** a native ssh client to be installed on
your laptop, as it uses the great [`asyncssh`
library](https://github.com/ronf/asyncssh) instead. However, it is
recommended to have one installed, if only for running an ssh agent,
as using ssh repeatedly is almost impossible without an ssh-agent.

You will see that in all the code of these tutorials, there is no
option to specify an alternate key. This is because all the examples
in this tutorial use **the set of keys known to your ssh agent**.

You can inspect and manage this set of keys using the `ssh-add`
command - at least on unix-based systems.

    # inspect current contents
    ~/.ssh $ ssh-add -l
    1024 SHA256:KNm0U4SgFV9bY957hJAIRR68n5AZHQ6e1gbiXrGHuOA /Users/parmentelat/.ssh/id_rsa (RSA)

    # if the key is not present in the list, just add it
    ~/.ssh $ ssh-add path/to/the/key/id_rsa.pub

    # check for the addition
    ~/.ssh $ ssh-add -l
    1024 SHA256:KNm0U4SgFV9bY957hJAIRR68n5AZHQ6e1gbiXrGHuOA /Users/parmentelat/.ssh/id_rsa (RSA)

### ssh-agent lifespan

In your ssh agent, the keys you add are kept **in memory**. This means
that they can only be added for the lifespan of the agent, and **need
to be added again** if, for example, you **log out of your session**,
or otherwise reboot your laptop.

### other means to deal with keys

The reasons we use keys from an ssh agent in the tutorial are:

* first it makes code a little simpler

* second, first in standard situations a private key is password
protected. And when a private key indeed is password-protected, then
using an ssh agent really becomes almost mandatory, because otherwise
you get prompted your password every single time you run an ssh
command.

However if you prefer, you can as well run without an ssh agent,
and tweak your script so that a specific key be used instead.

xxx we cannot give details at this point because it is too early;
to be added somewhere else towards the end.


</div>

</div> <!-- end div contents -->
