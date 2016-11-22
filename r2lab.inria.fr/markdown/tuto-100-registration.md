title: R2lab registration
tab: tutorial
skip_header: True
float_menu_template: r2lab/float-menu-tutorials.html

<script src="/assets/r2lab/open_tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#REGISTER">Register</a> </li>
  <li> <a href="#RESERVE">Reserve</a></li>
  <li> <a href="#ACCESS">Access</a></li>
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

If your organization is not listed in the portal, you can [request](https://portal.onelab.eu/portal/join) its addition (fig 1, <font color="red">**A**</font>).

In the keys form (fig 1, <font color="red">**B**</font>), make sure you select the **default/automatic:** option.
With this option, the Onelab portal generates a keypair for you, and you will need to download the corresponding **private key**.

In the rest of this tutorial, we assume that you store this private key in a file named `~/.ssh/onelab.private.`

**2 -** An email will be send to confirm your subscription. At this point you are a limited user. To gain full access you must **click at the link present** in the email confirmation and wait for the **manager organization validation** of your request. 

From that point you can login into the portal, [as described in the next tab](javascript:open_tab('RESERVE')).

</div>

<!------------ RESERVE ------------>
<div id="RESERVE" class="tab-pane fade" markdown="1">

Once you have signed up, you can log in the Onelab portal, which will lead you to the dashboard:

<br/>
<center>
![dashboard](/assets/img/dashboard.png)<br/>
Fig. 2 - The Onelab Dashboard
</center>

Before you can use any resource though, you must **create a new project** or **join a project** that already exists,
and select one of its **slices**. These concepts and how to interact with them are explained below.

### Project

A **project** is a sub-authority under the responsibility of your institution gathering users who will be able to create slices for their experiments.
Once logged in your dashboard a [create/join project](https://portal.onelab.eu/portal/project_request/) (fig 2, <font color="red">**A**</font>) project link is proposed and you can:

* **create new project** tab: In this option some informations for your new project are required.
Once this information is given the project could be submited.

* **join a project** tab: In this option a list of projects already created are proposed. Select the project you would like to join and confirm. 

An email confirmation resumes your action and your request will be send to authority manager validation.

### Slice

A **slice** is a set of testbed resources on which you can conduct an
experiment. You can request a new slice or either ask your colleagues
to give you access to an existing one.

*  **create a slice**:
Once logged, in your dashboard a **[request slice](https://portal.onelab.eu/portal/slice_request/)** (fig 2, <font color="red">**B**</font>) link is proposed. 
Once this information is given the slice could be required.

When a slice request is created, a confirmation email resumes your
action and your request will be send to authority manager
validation. Once the validation is done your dashboard present the
slices list (fig 2, <font color="red">**C**</font>) and the resource
reservation is available.

The resources could be reserved in some easy steps:

* Check the resources in the table list **or** click on the icon in the map.
* Select the resource using a table list (fig 3, <font color="red">**B**</font>) or using the map (fig 3, <font color="red">**A**</font>).
* Send the request using the submit button (fig 3, <font color="red">**C**</font>) and wait for the reservation. A progress message will appear.
* For each resource scheduled a slice time must be selected to operate in the resource. In ** scheduler tab, ** item (fig 3, <font color="red">**A**</font>)
it is possible book the resource. Once the scheduler tool is open, select your timeslot (fig 4)

<center>
![dashboard](/assets/img/slice_a.png)<br/>
Fig. 3 - Slice Dashboard
</center>

<center>
![dashboard](/assets/img/schedule_details.png)<br/>
Fig. 4 - Booking a node
</center>
</div>

<!------------ ACCESS ------------>
<div id="ACCESS" class="tab-pane fade" markdown="1">

Once the schedule has finished you can reach your node. In order to do it, the gateway is reachable by ssh connection.

1 - Connect to your account in faraday</strong>

    $ ssh onelab.your.slice.name@faraday.inria.fr

Example:

* Project Name: `onelab.inria.name`

* Slice Name: `tutorial`

* Your account: `onelab.inria.name.tutorial`

2 - Connect your node</strong>

    $ ssh root@fit10

In the next tutorial, we will [see in more details the available tools for manipulating the nodes](tuto-200-shell-tools.md#main).
      
3 - Troubleshooting

If you're getting a `Permission denied (publickey)` error, please check

* that you have correctly downloaded the private key from the OneLab portal into `~/.ssh/onelab.private`

* also please make sure that your ssh-agent is enabled, and add that key to it, by running:

    $ ssh-add ~/.ssh/~/.ssh/onelab.private

</div>

</div> <!-- end div contents -->




















