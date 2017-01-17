title: R2lab registration
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
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

### Entry point

The portal to register at R2lab is located at
[https://r2labapi.inria.fr/](https://r2labapi.inria.fr/).

Once in the website, in order to sign up at the onelab portal:

**1 -** Click in **Create an account** link (fig 1, <font color="red">**A**</font>).

**2 -** Fill the form with the requested info(fig 1, <font color="red">**B**</font>).
Special attention for the last field which must be selected as **INRIA** (fig 1, <font color="red">**C**</font>).

<center>
![register](/assets/img/register/new-1.png)<br/>
Fig. 1 - Register
</center>

**3 -** An email will be sent to confirm your subscription. At this
  point you are a *limited* user. To gain full access you must **click
  at the link present** in the email confirmation and wait for the
  manager in your organization to **validate your request**.

From that point you can login into the [portal](http://r2lab.inria.fr/index.md).
However, you need a slice. Let's move to the [next tab](javascript:open_tab('SLICE')) to create one.

</div>

<!------------ SLICE ------------>
<div id="SLICE" class="tab-pane fade" markdown="1">

### You need a slice

A **Slice** is a set of testbed resources on which you can conduct an
experiment. You can request a new slice by **sending us an email** (`fit-r2lab-dev@inria.fr`) with the name
you wish for your slice.

Your slice will have a composed name like:

*inria*_ **[the_name_you_have_asked]**

Note that you might have to **log out R2lab** and relog back in in order to see
newly created slices.

While your slice is created, take that chance to inform us of your public SSH key **puclic SSH key**.
We explain how to do it in the [next
tab](javascript:open_tab('CREDENTIALS')).

</div>

<!------------ R2LAB ------------>
<div id="CREDENTIALS" class="tab-pane fade" markdown="1">

### Attaching your SSH key to R2lab

Before start using R2lab platform, you'll need **attach your SSH key** to
R2lab. For this, let's follow 3 steps.

**1 - Generating the RSA key pair.**

  - Type in your terminal:

    $ `ssh-keygen -t rsa`

  - Once you have entered the `ssh-genkey` command, you will get a few more questions.
    To simplify, you can press enter and use the given default values.

  - The entire key generation process looks like this:
  <center>
  ![register](/assets/img/register/new-2.png)<br/>
  Fig. 2 - Key Pair
  </center>

  - The public key is now located in /home/**user-home**/.ssh/id_rsa**.pub**

  - Finally, include the new key pair to the agent, typing:

    $ `ssh-add -K /path/of/private/key`

**2 - Send us your public key.**

  In order to send us your **public key**, point your browser at [R2lab register](http://r2labapi.inria.fr/) site, then:

  - log in your account using the *email* and the *password* you already created.

  - Once inside your account, click the link **my account** located at the left panel (fig 3, <font color="red">**A**</font>).

  - The right panel will show your infos. Just below you will find a form to submit your public key (fig 3, <font color="red">**B**</font>). Click **browse** button and indicate the location of your public key in your filesystem.

    Note that, in general, the key pair is located under a hide folder (`../.ssh/`).
    In the browser view, after click *browse* button , enable the **hide file options view** to find it.

  - Confirm with the **updload key** button (fig 3, <font color="red">**C**</font>).

  <center>
  ![register](/assets/img/register/new-3.png)<br/>
  Fig. 2 - Uploading the SSH key
  </center>

Once this is done, you can [move to the next
tab](javascript:open_tab('RESERVATION')) to book your slices in R2lab.

</div>

<!------------ RESERVATION ------------>
<div id="RESERVATION" class="tab-pane fade" markdown="1">

### Make the reservation

In order to use R2lab, you must reserve the testbed. The right way to do this is
using the [R2lab UI](http://r2lab.inria.fr/run.md).
However, you must be logged in to see the reservation page.

Once in private area, just drag and drop the slice into the day calendar
(fig. 5, <fontcolor="red">**A**</font>) - (fig. 5, <font color="red">**B**</font>).
If you want dates in future, do the same action as described above but in the [complete
calendar](http://r2lab.inria.fr/book.md).

Other actions you can do in the calendar:

- If you want to **remove** or **cancel** your booking, just use double click in
the slice already booked;

- if you want to **move** the slice booked, drag and move the slice;

- if you want to **increase** or **decrease** in hours the duration of your slice,
just click and drag in the tiny line placed on the botton of each slice.
<br/>
<center>
![dashboard](/assets/img/schedule_details_1.png)<br/>
fig. 5 - Booking a slice in R2lab
</center>

When this is done, you can [move to the next tab](javascript:open_tab('ACCESS'))
to access R2lab platform and run your tests.

</div>


<!------------ ACCESS ------------>
<div id="ACCESS" class="tab-pane fade" markdown="1">

### Your Unix account

The name that you need to use to enter the testbed using SSH is the
name of the unix account that has been created for you. The name of
this unix account is simply the **slice name**.

For example, in this tutorial we have used the following names:

* slice name : `inria_tutorial`

* unix account / full slice name: `inria_tutorial`

At this point you should reach R2lab platform typing in your terminal:

$ `ssh` **your_slicename**`@faraday.inria.fr`

*<h6>if by any chance your public key is not at its standard location, then place `-i` option in the command line and inform the path of it.</h6>*

Once this command works for you, proceed to the next tutorial), where [we see in more details the available tools
for manipulating the nodes](tuto-200-shell-tools.md).

### Problems?

Feel free to contact us on [the R2lab users mailinglist
fit-r2lab-user@inria.fr](mailto:fit-r2lab-user@inria.fr) if you experience trouble with ssh-logging into the R2lab gateway at `faraday.inria.fr`, or with running your experiments, and/or none of those hints are helpful.

</div>

</div> <!-- end div contents -->
