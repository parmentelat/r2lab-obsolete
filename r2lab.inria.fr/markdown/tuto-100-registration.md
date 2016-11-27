title: R2lab registration
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#REGISTER">REGISTER</a> </li>
  <li> <a href="#GETKEY">GET KEY</a></li>
  <li> <a href="#RESERVE">RESERVE</a></li>
  <li> <a href="#ACCESS">ACCESS</a></li>

  << include r2lab/tutos-index.html >>
</ul>


<div id="contents" class="tab-content" markdown="1">

<!------------ REGISTER ------------>
<div id="REGISTER" class="tab-pane fade in active" markdown="1">

### Entry point
The official OneLab portal is located at [http://portal.onelab.eu](http://portal.onelab.eu).

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
next tab](javascript:open_tab('GETKEY')).

</div>

<!------------ GETKEY ------------>
<div id="GETKEY" class="tab-pane fade" markdown="1">

### Downloading the Onelab private key

Once you have signed up, you can log in the Onelab portal, which will lead you to the dashboard:

<br/>
<center>
![register](/assets/img/dashboard2.png)<br/>
Fig. 2 - Selecting the Account tab in the Onelab dashboard
</center>

When you create your user, the Onelab portal generates a keypair for
you, and the next thing we will do is to download the corresponding
**private key**.

From the dashboard, click the `Account` tab (fig. 2, <font
color="red">**A**</font>), and from there download that private key.

In the rest of this tutorial, we assume that you store this private
key in a file named `~/Downloads/onelab.private`. You can choose any
other location that is convenient for you, just make sure to write
down where it is stored because we will need this later on when we set up our ssh credentials.

When this is done, you can [move to the next
tab](javascript:open_tab('RESERVE')) to create our account on R2lab.

</div>

<!------------ RESERVE ------------>
<div id="RESERVE" class="tab-pane fade" markdown="1">


<br/>
<center>
![dashboard](/assets/img/dashboard.png)<br/>
fig. 3 - The Onelab Dashboard
</center>

Before you can use any resource though, you must **create a new project** or **join a project** that already exists,
and select one of its **slices**. These concepts and how to interact with them are explained below.

### Project

A **project** is a sub-authority under the responsibility of your institution gathering users who will be able to create slices for their experiments.
Once logged in your dashboard a [create/join project](https://portal.onelab.eu/portal/project_request/) (fig. 3, <font color="red">**A**</font>) project link is proposed and you can:

* **create new project** tab: In this option some informations for your new project are required.
Once this information is given the project could be submited.

* **join a project** tab: In this option a list of projects already created are proposed. Select the project you would like to join and confirm. 

An email confirmation resumes your action and your request will be send to authority manager validation.

### Slice

A **slice** is a set of testbed resources on which you can conduct an
experiment. You can request a new slice or either ask your colleagues
to give you access to an existing one.

*  **create a slice**:
Once logged, in your dashboard a **[request slice](https://portal.onelab.eu/portal/slice_request/)** (fig. 3, <font color="red">**B**</font>) link is proposed. 
Once this information is given the slice could be required.

When a slice request is created, a confirmation email resumes your
action and your request will be send to authority manager
validation. Once the validation is done your dashboard present the
slices list (fig. 3, <font color="red">**C**</font>) and the resource
reservation is available.

The resources could be reserved in some easy steps:

* Check the resources in the table list **or** click on the icon in the map.

* Select the (single) resource attached to R2lab using the table list
  (fig. 4, <font color="red">**B**</font>) or using the map (fig. 4,
  <font color="red">**A**</font>). The node that needs to be chosen
  here is named `37nodes.r2lab`, you can find it easily by typing
  `37nodes` in the search area.

* Send the request using the submit button (fig. 4, <font
  color="red">**C**</font>) and wait for the reservation. A progress
  message will appear.

<br/>
<br/>
<center>
![dashboard](/assets/img/slice_a.png)<br/>
fig. 4 - Attaching R2lab to your slice
</center>

### Reservation

Optionnally, you can use the onelab portal to reserve the
testbed. This is currently not the recommended method, as this feature
is available right from the R2lab website as well.

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

<!------------ ACCESS ------------>
<div id="ACCESS" class="tab-pane fade" markdown="1">

From the moment where you have successfully attached your slice to
R2lab, you should be able to reach the R2lab testbed by ssh.

### your Unix account 

The name that you need to use to enter the testbed using ssh is the
name of the Unix account that has been created for you.
The name of this Unix account is simply the name of your project, with the slice name appended with a `.`

For example, in this tutorial we have used the following names:

* Project: `onelab.inria.r2lab`

* Slice : `tutorial`

* Unix account: `onelab.inria.r2lab.tutorial`

### ssh with your private key

Remember [that we had stored the private key](javascript:open_tab('GETKEY')) in `~/Downloads/onelab.private`. 

So we are ready to try it all out - of course you will need to replace `onelab.your.slice.name` here

    cd ~/Downloads
    chmod 600 onelab.private
    ssh -i onelab.private onelab.your.slice.name@faraday.inria.fr id

This should run the `id` command on `faraday.inria.fr` and output something like this

    $ ssh -i /dev/null onelab.inria.r2lab.tutorial@faraday.inria.fr id
    uid=1102(onelab.inria.r2lab.tutorial) gid=1102(onelab.inria.r2lab.tutorial) groups=1102(onelab.inria.r2lab.tutorial)

### Troubleshooting

**Do not proceed** with this tutorial until this command works fine. When it does you can skip to the next section

Here is a list of things to double check if it foes not:

* xxx here a trouble shooting section

### add your pricate key to the ssh agent

xxx what is an agent; why is it useful

reconcile this with tuto-300xxx

Need to also

* add key to ssh-agent

* re-run sh with -i /dev/null this time

xxx here

In the next tutorial, we will [see in more details the available tools
for manipulating the nodes](tuto-200-shell-tools.md#main).
      
it means that you
are not properly registered with the testbed. In this case, please
make sure that

* you have obtained an account and a project at the Onelab portal
* you have associated the R2lab meta-node named `37-nodes` to your
  project in the Onelab resources page
* you have downloaded the private key from Onelab, and installed it in `~/.ssh/onelab.private` with proper permissions (typically `chmod 600`)

Feel free to contact us on [the R2lab users mailinglist fit-r2lab-user@inria.fr](mailto:fit-r2lab-user@inria.fr) if none of this is helpful.

xxx here

### Troubleshooting

If you're getting a `Permission denied (publickey)` error, please check

* that you have correctly downloaded the private key from the OneLab portal into `~/.ssh/onelab.private`

* also please make sure that your ssh-agent is enabled, and add that key to it, by running:

    $ ssh-add ~/.ssh/~/.ssh/onelab.private

</div>

</div> <!-- end div contents -->
