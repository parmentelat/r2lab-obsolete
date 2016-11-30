title: nepi-ng - managing files
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#C1">C1</a></li>
  <li> <a href="#C2">C2</a></li>
  <li> <a href="#C2">C3</a></li>
  <li> <a href="#WRAPUP">WRAPUP</a></li>

  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

In this series, we will see how to transfer files between hosts, using
the `Push` and `Pull` commands in a `SshNode`.

We will also take this chance to see that a `SshJob` object can be
defined with several commands if that's helpful, avoiding the need to
create long strings of jobs.

Let us start with [copying files over to the nodes](javascript:open_tab('C1')).

</div>

<!------------ C1 ------------>
<div id="C1" class="tab-pane fade" markdown="1">

### Objective

We start over from scratch here, and to begin with, we want to

* locally generate a random file that is 1 Mb large,
* and push it over to node fit01

This is what the code below carries out; the things to outline in this code are

* the local commands are in this version executed using low-level
  tools, it is a little awkward, and we plan on providing as part of
  `apssh` tools similar to `SshJob` to achieve the same result in a more elegant way

* once the local file is created, we use a `Push` instance instead of
  the `Run` and its variants that we have seen so far, to actually
  copy local files on the remote node;

* also note that inside a single `SshJob` instance, it is possible to
  provide an (ordered) list of commands to ron on that node, mixing
  commands and file transfers as needed; this is how we can both push
  the `RANDOM` file over to node1, and display its size and SHA1 sum,
  using a single instance of `SshJob`.

### The code

<< codeview C1 C1-files.py >>

### Sample output

    $ python3 ./C1-files.py
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1048576 Nov 30 21:32 RANDOM
    LOCALNODE:3f147d42ed40df83819de3ab2093de352a1c5c6b  RANDOM
    fit01:-rw-r--r-- 1 root root 1048576 Nov 30 21:32 RANDOM
    fit01:3f147d42ed40df83819de3ab2093de352a1c5c6b  RANDOM

### Next

In [the next section](javascript:open_tab('C2')) we will see
how to retrieve back that same file in order to close the loop.

</div>

<!------------ C2 ------------>
<div id="C2" class="tab-pane fade" markdown="1">

### Objective

### The code

<< codeview C2 C1-files.py C2-files.py >>

### Sample output

### Next
[](javascript:open_tab('C3'))

</div>

<!------------ C3 ------------>
<div id="C3" class="tab-pane fade" markdown="1">

### Objective

### The code

<< codeview C3 C2-files.py C3-files.py >>

### Sample output

### Next
[](javascript:open_tab('WRAPUP'))

</div>

<!------------ WRAPUP ------------>
<div id="WRAPUP" class="tab-pane fade" markdown="1">

</div>

</div> <!-- end div contents -->
