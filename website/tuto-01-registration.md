title: Registration Tutorial
tab: tutorial
---

### Entry point
The official OneLab portal is located at [http://portal.onelab.eu](http://portal.onelab.eu).

Note there is also a [development portal](http://dev.myslice.info) that is also connected to R2Lab, but usage should be restricted in theory.

<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
  
  <div class="panel panel-default">
    <div class="panel-heading" role="tab" id="headingOne">
      <h4 class="panel-title">
        <a role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
          Make your registration
        </a>
      </h4>
    </div>
    <div id="collapseOne" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingOne">
      <div class="panel-body">
      	To proceed your registration at onelab portal:
      	<br>
      	<br>
				**1 -** Fill the form with the requested info. Organization, first name, etc ... . 
				<br>
				<br>
				<center>
				![register](assets/img/register.png)<br>
				Fig. 1 - Register
				</center>
				<br>
				If your organization is not listed in the portal, you can [request](https://portal.onelab.eu/portal/join) its addition (fig 1, <font color="red">**A**</font>).
				<br>
				In the keys form (fig 1, <font color="red">**B**</font>), you'll find two options:
				<br>
				<br>
				**default/automatic:** Choose this option if you have no keys generated in your device or if you are not an advanced user. In case of any doubts about the keys process, this option is recommended as well.
				<br>
				With this policy choice selected the portal will generate and manage the key pair identity for you.
				<br>
				<br>
				**advanced/manual:** Choose this option if you have knowledge about keys pairs and you already have them generated.
				<br>
				A file button is provided to search at your computer your correspondent key and upload to the portal.
				Once chosen the manual delegation of credentials option, a **[complementary step](https://portal.onelab.eu/portal/manual_delegation)** is required. This step can be done after the validation of your account by the manager of your organization.
				<br>
				<br>
				**2 -** An email will be send to confirm your subscription. At this point you are a limited user. To gain full access you must **click at the link present** in the email confirmation and wait for the **manager organization validation** of your request.
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading" role="tab" id="headingTwo">
      <h4 class="panel-title">
        <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
          Reserve the resources for your experiments
        </a>
      </h4>
    </div>
    <div id="collapseTwo" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingTwo">
      <div class="panel-body">
				In order to use the plataform, run and play your experiments, you must **create a new project** or **join a project** that already exists and book an **slice** inside of it. These concepts and how to interact with them are explained as follows.
				<br>
				<br>
				<center>
				![dashboard](assets/img/dashboard.png)<br>
				Fig. 2 - Dashboard
				</center>
				<br>
				<h3>Project</h3>
				A **project** is a sub-authority under the responsibility of your institution gathering users who will be able to create slices for their experiments.
				Once logged in your dashboard a **[create/join project](https://portal.onelab.eu/portal/project_request/)** (fig 2, <font color="red">**A**</font>) project link is proposed and you can:
				<br>
				<br>
				- **create new project** tab: In this option some informations for your new project are required.
				Once this information is given the project could be submited.
				<br>
				<br>
				- **join a project** tab: In this option a list of projects already created are proposed. Select the project you would like to join and confirm. 
				<br>
				An email confirmation resumes your action and your request will be send to authority manager validation.
				<br>
				<h3>Slice</h3>
				A **slice** is a set of testbed resources on which you can conduct an experiment. You can request a new slice or either ask your colleagues to give you access to an existing one.
				<br>
				<br>
				- **create a slice**: Once logged, in your dashboard a **[request slice](https://portal.onelab.eu/portal/slice_request/)** (fig 2, <font color="red">**B**</font>) link is proposed. 
				Once this information is given the slice could be required.
				<br>
				When a slice request is created, a confirmation email resumes your action and your request will be send to authority manager validation.
				Once the validation is done your dashboard present the slices list (fig 2, <font color="red">**C**</font>) and the resource reservation is available.
				<br>
				<br>
				The resources could be reserved in some easy steps:
				<ul>
					<li>Check the resources in the table list **or** click on the icon in the map.</li>
					<li>Select the resource using a table list (fig 3, <font color="red">**B**</font>) or using the map (fig 3, <font color="red">**A**</font>).</li>
					<li>Send the request using the submit button (fig 3, <font color="red">**C**</font>) and wait for the reservation. A progress message will appear.</li>
					<li>For each resource scheduled a slice time must be selected to operate in the resource. In ** scheduler tab, ** item (fig 3, <font color="red">**A**</font>) is possible book the resource. Once the scheduler tool is open, select the range time of your interest (fig 4)</li>
				</ul>
				<br>
				<center>
				![dashboard](assets/img/slice_a.png)<br>
				Fig. 3 - Slice Dashboard
				</center>
				<br>
				<br>
				<center>
				![dashboard](assets/img/schedule_details.png)<br>
				Fig. 4 - Booking a node
				</center>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading" role="tab" id="headingThree">
      <h4 class="panel-title">
        <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
          Access your nodes
        </a>
      </h4>
    </div>
    <div id="collapseThree" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingThree">
      <div class="panel-body">
        Once the schedule has finished you can reach your node. In order to do it, the gateway is reacheble by ssh connection.
        <br>
        <br>
        
        <b>1 - Connect to your account in faraday</b>
        <p>
        	<pre class="hljs"><code>$ ssh your_account@faraday<span class="hljs-class">.inria</span><span class="hljs-class">.fr</span></code></pre>
      	</p>
      	<h6>
      		Note that your account name is composed by: <b>project name"."slice name</b>.
      		<br>
      		<br>
      		<p>
		      	Example:<br>
		      	<b>Project Name:</b> onelab.inria.name<br>
		      	<b>Slice Name:</b> tutorial<br>
		      	<b>Your account</b>: onelab.inria.name.tutorial
	      	</p>
      	</h6>

        <b>2 - Connect your node</b>
				<p>
        	<pre class="hljs"><code>$ ssh root@your_reserved_resource</span></code></pre>
        </p>
      	<h6>

      		<p>
      		Example:<br>
		      ssh root@fit10
		      <br>
		      ssh root@fit26
		    	</p>
      	</h6>

      	[See more](tuto-02-michelle.html) how to manipulate the nodes.
      	</p>
      
      	<b>3 - Troubleshooting</b>
				<p>
      	<p>If you have the <code>Permission denied (publickey).</code> error, check if you correctly pasted your public key on the OneLab portal.
      	Alternatively, restart the tutorial registration from the beginning.</p>

      </div>
    </div>
  </div>
  
</div>






