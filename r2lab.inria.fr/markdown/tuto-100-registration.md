title: R2lab registration
tab: tutorial
skip_header: True

<script src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/3.2.0/diff.min.js"></script>
<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#REGISTER">1- REGISTER</a> </li>
  <li> <a href="#SLICE">2- SLICE</a></li>
  <li> <a href="#CREDENTIALS">3- CREDENTIALS</a></li>
  <li> <a href="#RESERVATION">4- RESERVATION</a></li>
  <li> <a href="#ACCESS">5- ACCESS</a></li>

  << include r2lab/tutos-index.html >>
</ul>


<div id="contents" class="tab-content" markdown="1">

<!------------ REGISTER ------------>
<div id="REGISTER" class="tab-pane fade in active" markdown="1">

### Introduction

First of all, welcome to R2lab.

For the time being, R2lab’s operations rely on 2 separate websites:

* **Reservation Portal** at https://r2lab.inria.fr : is the one used for daily operations,
like getting a reservation, and live monitoring of nodes status.
Since 2017 April, you can also manage your ssh keys from this site.

* **Register Portal** at https://r2labapi.inria.fr : is the backend that manages accounts,
so you will be requested to interact with this site only once, when requesting an account.

Both sites share the same *email*/*password* credentials.

### Entry point

In order to register at r2lab:

1. start from our Register Portal,
and specifically [the registration page](https://r2labapi.inria.fr/db/persons/register.php)
(or click the  **Create an account** link - fig 1, <font color="red">**A**</font> - if you arrive from the home page).

1. at that point just fill in the form, as shown below (fig 1, <font color="red">**B**</font>).

1. please pay special attention to the last field labeled *Site*,
which should be selected as **INRIA** (fig 1, <font color="red">**C**</font>),
unless your organization appears in the list already.

1. An email will be sent to confirm your subscription. At this
  point you are a *limited* user. To gain full access you must **click
  the link present** in the confirmation email, and wait for the
  manager in your organization to **validate your request**.

<center>
![register](/assets/img/tuto-register-1.png)<br/>
Fig. 1 - Register
</center>

From that point you can login into the [Reservation Portal](http://r2lab.inria.fr/index.md).
However, you need a slice. Let's move to the [next tab](javascript:open_tab('SLICE')) to create one.

</div>

<!------------ SLICE ------------>
<div id="SLICE" class="tab-pane fade" markdown="1">

### You need a slice

A **Slice** is a set of testbed resources on which you can conduct an experiment.
A slice is attached to one or several users who will all be granted access to the testbed during the reserved timeslot.

You can request a new slice by
[sending us an email to fit-r2lab-dev@inria.fr](mailto:fit-r2lab-dev@inria.fr?subject=new slice request)

Please make sure to mention

* a desired slice name - the actual slicename will look like `inria_`*thename_you_ask*
* a few lines of free text describing your experiment
* a URL that points at that experiment - as far as possible - or at your research group if the experiment does not have a website.


While your slice is created, take that chance to upload your public SSH key so that we can grant you access.
We explain how to do it in the [next tab](javascript:open_tab('CREDENTIALS')).

</div>

<!------------ R2LAB ------------>
<div id="CREDENTIALS" class="tab-pane fade" markdown="1">

### Uploading your SSH public key to R2lab

Before you can start using the R2lab testbed, you'll need to **upload your SSH public key** to
R2lab. For this, let's follow 2 steps.

### 1 - Generating an RSA key pair

  - If you do not have a public key already, type in your terminal:

    $ `ssh-keygen -t rsa`

  - Once you have entered the `ssh-keygen` command, you will get a few more questions.
    To simplify, you can press enter and use the given default values.

  - The entire key generation process looks like this:
  <center>
  ![register](/assets/img/tuto-register-2.png)<br/>
  Fig. 2 - Generating a key pair
  </center>

  - The public key is now located under your home directory in `~/.ssh/id_rsa.pub`

### 2 - Upload your public key

  In order to send us your **public key**, point your browser at the [r2lab website](http://r2lab.inria.fr/), then:

  - Log in your account using the *email*/*password* you already created;

  - Once inside your account, go to either the *BOOK* or *RUN* pages, and click the "slices & keys <span class='fa fa-gear'></span>" link
   (fig 3, <font color="red">**A**</font>), which will pop a dialog dedicated to managing your slices and keys.
   If your public key is not listed there, use the "*Select public key file to add*" button
   (fig 3, <font color="red">**B**</font>) to choose the file that contains your public key,
   that will then be uploaded.

### Please note:

  - if you are not familiar with ssh keys, please be careful to **always select the public key**;
    the private key, as its name clearly states, is not supposed to be uploaded anywhere;
    
  - in general, the key pair is located under a hide folder (`../.ssh/`).
    In the browser view, after click *browse* button , enable the **hide file options view** to find it;

  - under Windows, we have experienced issues when dealing with keys originating from the `putty`
    application; if this is your case we recommend that you generate another key pair with a more
    standard format.

  <center>
  ![register](/assets/img/tuto-register-3.png)<br/>
  Fig. 3 - Uploading your SSH key
  </center>

Once this is done, you should see something like on fig. 4 below

  <center>
  ![register](/assets/img/tuto-register-4.png)<br/>
  Fig. 4 - An uploaded SSH key
  </center>


You can then [move to the next
tab](javascript:open_tab('RESERVATION')) to book your slices in R2lab.

</div>

<!------------ RESERVATION ------------>
<div id="RESERVATION" class="tab-pane fade" markdown="1">

### Make the reservation

In order to use R2lab, you must reserve the testbed. The right way to do this is
using our [Reservation Portal - UI](http://r2lab.inria.fr/run.md).
However, you must be logged in to see the reservation page.

Once in private area, just drag and drop the slice into the day calendar
(fig. 5, <font color="red">**A**</font>) - (fig. 5, <font color="red">**B**</font>).

If you want dates in future, do the same action as described above but in the [Reservation Portal - Calendar](http://r2lab.inria.fr/book.md).

Other actions you can do in the calendar:

- If you want to **remove** or **cancel** your booking, just use double click in
the slice already booked;

- if you want to **move** the slice booked, drag and move the slice;

- if you want to **increase** or **decrease** in hours the duration of your slice,
just click and drag in the tiny line placed on the botton of each slice.
<br/>
<center>
![dashboard](/assets/img/tuto-reservation.png)<br/>
fig. 5 - Booking a slice in R2lab
</center>

When this is done, you can [move to the next tab](javascript:open_tab('ACCESS'))
to access R2lab platform and run your tests.

</div>


<!------------ ACCESS ------------>
<div id="ACCESS" class="tab-pane fade" markdown="1">

### The ssh agent

This step is optional, but worth reading for beginners.

When accessing R2lab, you will be authenticated through ssh.
Your public key is installed and authorized on the R2lab end, and in order
to establish that you are who you claim to be, you (i.e. your computer)
will be challenged so as to prove that you can access the corresponding private key.

When multiple ssh connections are created, it is traditionally easier
to run an ssh agent. The role of this software, that runs locally on
your laptop, is to work as a cache of private keys, so that you only
need enter the password for your private key once when you log in into
your laptop, rather than each time an ssh session is created - which
can happen a lot.

This is why, before you try to enter the R2lab gateway using your slice,
we recommend that you add your ssh **private** key in your ssh agent, for example

   # in order to list the keys currently loaded in the agent
   $ ssh-add -l
   # in order to add one
    $ ssh-add -K ~/.ssh/id_rsa


### Your Unix account

The name that you need to use to enter the testbed using SSH is the
name of the unix account that has been created for you. The name of
this unix account is simply the **slice name**.

For example, in this tutorial we have used the following names:

* slice name : `inria_tutorial`

* unix account / full slice name: `inria_tutorial`

At this point you should reach R2lab platform typing in your terminal:

    $ ssh inria_your_slice_name@faraday.inria.fr

*<h6>if by any chance your public key is not at its standard location, and not known to your ssh agent, then place `-i` option in the command line to specify its path.</h6>*

Once this command works for you, proceed to the next tutorial, where [we see in more details the available tools
for manipulating the nodes](tuto-200-shell-tools.md).

### Problems?

Feel free to contact us on the **R2lab users mailinglist** [fit-r2lab-users@inria.fr](mailto:fit-r2lab-user@inria.fr) if you experience trouble with ssh-logging into the R2lab gateway at `faraday.inria.fr`, or with running your experiments, and/or none of those hints are helpful.

</div>

</div> <!-- end div contents -->
