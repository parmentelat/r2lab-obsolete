# routine to test my slice
The related document aims test all user steps to have an account at OneLab portal and posteriori schedule resources in the R2lab platform.

If you are already registered, have a project approved and a slice created, you can start directly ate item 4.
  
### 1. registration
1. Point the browser at **https://portal.onelab.eu**.
2. Click at button **sign up** at right-down in the page.
3. Type or select the **organization** then fill the form with **name**, **surname**, **email**, **password**.
4. Select **recommended option** in the ssh-key option.
5. Click **sign up**.
6. Wait for a confirmation **email**. Once the email arrives, to confirm your subscription, click at the link present in the email body. 
Upon confirmation of your signup request, an email will be send to the manager at your organization asking a validation request.

### 2. creating a project
1. Once logged-in, at the dashboard click the link **create/join project**. Fill project's **name**, **authority**, **url** and **description** of it.
2. Click **sign up**.
3. You will receive an email as soon as your request is validated by a manager. Once your project is validated you may view it on your dashboard.

### 3. creating a slice
1. After create or join a project, click the link **create slice** and fill slice's **name** and the **project** related to the slice.

### 4. managing slices

1. At the **resources**, already selected, uncheck all items at the left panel (**facilities**), except by FitR2Lab item.
2. At the list located at **table** tab, which are already selected,  check the box related to **37nodes.r2lab** item.
3. Click **apply** button.
4. A panel will open. Wait for the message **success** in the status column to close the panel.
5. After the loading message finish, click at **scheduler** tab.
6. Click in the **square time slot** to **select**/**unselect** your book time preference.
7. Once selected the time slots, click **apply** button and wait for the status message confirmation with **success** to click at the **close** button.
8. The previously white spaces should be at this point **blue**. This indicate that the time slot was booked correctly.

### 5. ssh to the gateway
1. Open your terminal and type: ssh your-slice-user@faraday.inria.fr. You can find your user at top (under OneLab logo) of slice reservation. screen. A message **Welcome to Ubuntu 14.04.3 LTS...** will appear.

### 6. load an O.S. image in the resources
1. Type in gateway terminal **rload 3 -i fedora-21.ndz** to load fedora 21 at node number 3.
2. Type in the gateway terminal **nodes 3** to select the node. Type **releases** to check if you reach the node and check the O.S version loaded.
