title: R2lab registration
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#REGISTER">REGISTER</a> </li>
  <li> <a href="#SLICE">SLICE</a></li>
  <li> <a href="#R2LAB">R2LAB</a></li>
  <li> <a href="#GETKEY">GET KEY</a></li>
  <li> <a href="#ACCESS">ACCESS</a></li>

  << include r2lab/tutos-index.html >>
</ul>


<div id="contents" class="tab-content" markdown="1">

<!------------ REGISTER ------------>
<div id="REGISTER" class="tab-pane fade in active" markdown="1">

### Entry point

The official OneLab portal is located at
[http://portal.onelab.eu](http://portal.onelab.eu).

In order to sign up at the onelab portal:

**1 -** Fill the form with the requested info. 

<center>
![register](/assets/img/register.png)<br/>
Fig. 1 - Register
</center>

If your organization is not listed in the portal, you can
[request](https://portal.onelab.eu/portal/join) its addition (fig 1,
<font color="red">**A**</font>).

In the keys form (fig 1, <font color="red">**B**</font>), make
sure you select the **default/automatic:** option.  

**2 -** An email will be sent to confirm your subscription. At this
  point you are a limited user. To gain full access you must **click
  at the link present** in the email confirmation and wait for the
  manager in your organization to **validate your request**.

From that point you can login into the portal, [and move to the
next tab](javascript:open_tab('SLICE')).

</div>

<!------------ SLICE ------------>
<div id="SLICE" class="tab-pane fade" markdown="1">

### You need a slice

Once you have signed up, you can log in the Onelab portal, which will
lead you to the dashboard:

<br/>
<center>
![dashboard](/assets/img/dashboard.png)<br/>
fig. 3 - The Onelab Dashboard
</center>

Before you can use any resource, you must **create a new project** or
**join a project** that already exists, and select one of its
**slices**. These concepts and how to interact with them are explained
below.

### Project

A **project** is a sub-authority under the responsibility of your
institution gathering users who will be able to create slices for
their experiments.  
Once logged in your dashboard, the [create/join
project](https://portal.onelab.eu/portal/project_request/) (fig. 3,
<font color="red">**A**</font>) link allows you to:

* **create new project** tab: In this option some informations for
your new project are required.  Once this information is given the
project could be submited.

* **join a project** tab: In this option a list of projects already
    created are proposed. Select the project you would like to join
    and confirm.

An email confirmation resumes your action and your request will be
send to authority manager validation.

### Slice

A **slice** is a set of testbed resources on which you can conduct an
experiment. You can request a new slice, or ask your colleagues to
give you access to an existing one.

This can be done throught the **[request
slice](https://portal.onelab.eu/portal/slice_request/)** (fig. 3,
<font color="red">**B**</font>) link.

When a slice request is created, a confirmation email is sent to a
manager within your institution for validation. Once the validation is
done your dashboard shows you (fig. 3, <font color="red">**C**</font>)
the list of all slices where you belong. Note that you might have to
**log out of Onelab** and relog back in in order to see newly created
slices. Clicking on one of these slices will lead you to the slice
dashboard, as you can see [on fig. 4 in the next
tab](javascript:open_tab('R2LAB')).

</div>

<!------------ R2LAB ------------>
<div id="R2LAB" class="tab-pane fade" markdown="1">

### Attaching your slice to R2lab

At that point, your slice is still unknown to R2lab. Before you can
use that slice for entering R2lab, you need to **attach it** to
R2lab. For this, from the slice dashboard depicted in fig. 4 below,
simply

* Select the (single) resource attached to R2lab using the table list
  (fig. 4, <font color="red">**B**</font>) or using the map (fig. 4,
  <font color="red">**A**</font>). The node that needs to be chosen
  here is named `37nodes.r2lab`, you can find it easily by typing
  `37nodes` in the search area (below the <font color="red">**A**</font> mark)

* Send the request using the submit button (fig. 4, <font
  color="red">**C**</font>) and wait for the answer, that can take a
  little while.

Once this is done successfully, you can [go to the next
tab](javascript:open_tab('GETKEY')) to see how to obtain your Onelab
key.

<br/>
<center>
![dashboard](/assets/img/slice_a.png)
<br/><br/>
fig. 4 - Attaching R2lab to your slice
</center>

### Reservation

Optionnally, you can use the onelab portal to reserve the
testbed. This is currently not the recommended method, as this feature
is available right from the R2lab website as well (see the [book.md]
page if you are currently logged in).

For each resource scheduled a time slot must be selected to operate in
the resource.

This is done in the **scheduler tab** (fig. 4, <font
color="red">**A**</font>), which leads you to fig. 5:

<br/>
<br/>
<center>
![dashboard](/assets/img/schedule_details.png)<br/>
fig. 5 - Booking a node from Onelab
</center>
</div>

<!------------ GETKEY ------------>
<div id="GETKEY" class="tab-pane fade" markdown="1">

### Downloading the Onelab private key

When you create your user, the Onelab portal generates a keypair for
you, and the next thing we will do is to download the corresponding
**private key**.

From the dashboard, click the `Account` tab (fig. 2, <font
color="red">**A**</font>), and from there download that private key.

<br/>
<center>
![register](/assets/img/dashboard2.png)<br/>
Fig. 2 - Selecting the Account tab in the Onelab dashboard
</center>

In the rest of this tutorial, we assume that you store this private
key in a file named `~/Downloads/onelab.private`. You can choose any
other location that is convenient for you, just make sure to write
down where it is stored because we will need this later on when we set
up our ssh credentials.

When this is done, you can [move to the next
tab](javascript:open_tab('RESERVE')) to create our account on R2lab.

</div>

<!------------ ACCESS ------------>
<div id="ACCESS" class="tab-pane fade" markdown="1">

From the moment where you have both (i) successfully attached your
slice to R2lab, and (ii) downloaded your Onelab key, you should be
able to reach the R2lab testbed by ssh.

### Your Unix account 

The name that you need to use to enter the testbed using ssh is the
name of the Unix account that has been created for you.  The name of
this Unix account is simply the name of your project, with the slice
name appended with a `.`

For example, in this tutorial we have used the following names:

* project: `onelab.inria.r2lab`

* slice name : `tutorial`

* unix account / full slice name: `onelab.inria.r2lab.tutorial`

### ssh with your private key

Remember [that we had stored the private
key](javascript:open_tab('GETKEY')) in `~/Downloads/onelab.private`.

So we are ready to try it all out :

    cd ~/Downloads
    chmod 600 onelab.private
    ssh -i onelab.private onelab.your.slice.name@faraday.inria.fr id

This should run the `id` command on `faraday.inria.fr` and output
something like this

    $ ssh -i /dev/null onelab.inria.r2lab.tutorial@faraday.inria.fr id
    uid=1102(onelab.inria.r2lab.tutorial) gid=1102(onelab.inria.r2lab.tutorial) groups=1102(onelab.inria.r2lab.tutorial)


Once this command works for you, proceed to the next tutorial), where [we see in more details the available tools
for manipulating the nodes](tuto-200-shell-tools.md).
      
### Troubleshooting

**Do not proceed** with this tutorial until this command works fine. When it does you can skip to the next section

Here is a list of things to double check if it does not:

* Did you attach the R2lab `37nodes` metanode to your slice ?

* Does file `onelab.private` exist and contain the **private** key as
  downloaded from the Onelab portal ?

* Does it have the right permissions (in essence, others than you
  should not be able to read it)

* Was this Unix account properly created at R2lab ?
  **NOTE**: as of 2016 end of November, a known glitch seems to prevent this to work properly. 

Feel free to contact us on [the R2lab users mailinglist
fit-r2lab-user@inria.fr](mailto:fit-r2lab-user@inria.fr) if you cannot
reach the point where this ssh command works out, and none of those hints are
helpful.

</div>

</div> <!-- end div contents -->
