title: nepi-ng - in real scale
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#MULTI_PING">MULTI_PING</a></li>

  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

# Contents

We have grouped in this page a few more elaborate examples :

* a `multi-ping` example that in particular deals with a variable
  number of nodes, and runs ping beween each couple of nodes.

* more examples are expected in the future...

</div>

<!------------ MULTI_PING ------------>
<div id="MULTI_PING" class="tab-pane fade" markdown="1">

## Objective

This script is an extension of the B series, but the number of nodes
involved is now a parameter in the experiment (the `--max` option that
defaults to 5).

We will thus use the `m` first nodes in the system, and

* initialize the wireless ad-hoc network, on all those node, like we had done in the `B` series,
* and then run as many pings as there are couples of nodes - that is to say `m*(m-1)/2`  pings
* the results of these are then retrieved locally in files names `PING-i-j`

## `--parallel` : 3 modes: sequential, full parallel, partially parallel

This script implements 3 different strategies, mostly for
the purpose of this tutorial:

### sequential (default) :

  * check that we have the lease,
  * then prepare all nodes (init their wireless ad-hoc network) in parallel,
  * then **sequentially** run all the pings
  
### full parallel (with the `-p 0` option) :

Same, but all the pings are running **at the same time**.  This is
why, as you will realize if you try to run the script yourself, this
strategy can cope with something like around 8 nodes. With a higher
number of nodes, there is a too great need of simultaneous open
connections, and the script stops to behave as expected.

### parallel / limited window - with the .e.g `-p 20` option :

This is an illustration of the ability that an `asynciojobs` scheduler
has, to limit the number of simultaneous jobs. So if you say `-p 20`
only a maximum number of 20 pings will run at the same time. 

## `--dry-run`

This script also implements a dry-run mode. If the `-n` option is
provided, the scheduler is merely printed out in text form, and a
`.dot` file is also produced, as well as a `.png` file if you have
`dot` installed on your system.

Here are the outputs obtained with `--max 4`. As you can see on these
figures, the only difference between both strategies is the addition
of one `required` relationship per ping job. This is what the
`Sequence` object is only about, [see more details on `Sequence`
in its own documentation](http://nepi-ng.inria.fr/asynciojobs/API.html#module-asynciojobs.sequence).


<div class="row" markdown="1">
<div class="col-md-4">  
<center><img src="assets/img/multi-ping-seq-4.png" width="100%">
<br/><br/>Sequential scheduler with `--max 4`</center>
</div>  
<div class="col-md-8" markdown="1">  
<center><img src="assets/img/multi-ping-par-4.png" width="100%">
<br/><br/>Parallel scheduler with `--max 4`</center>
</div>
</div>


## troubleshooting: `--verbose` and `--debug` 

The script implements 2 options to increase verbosity

* `-v/--verbose` sets verbosity of the ssh layer, like we have done
  throughout these tutorials, and
* `-d/--debug` sets verbosity on the scheduler and jobs objects.

That's one way to see it, but your specific needs may lead you to
doing other choices.


### The code

<< codeview MULTI_PING multi-ping.py >>

### How to run it

How to produce the 2 figures above:

    # sequential
    ./multi-ping.py -m 4 -n
    # parallel
    ./multi-ping.py -m 4 -p 0 -n


</div>

</div> <!-- end div contents -->
