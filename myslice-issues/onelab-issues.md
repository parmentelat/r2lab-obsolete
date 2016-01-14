# OneLab Report
The related document aims present all bugs and issues of all user steps to have an account at OneLab portal and posteriori schedule resources in the R2lab platform.

When I try to select two resources and apply for the reservation a mysterious message appears. To fix it you must logout and login again or reload the page.

![alt tag](img/1.png)

After had selected the slice correctly with the resource scheduled I had problems with public key.
nano$ ssh onelab.inria.mario.tutorial@faraday.inria.fr
Permission denied (publickey)

After select the "37nodes.r2lab" resources and click apply button the status was failure. This was in the first day tests.
It was fixed, but come back again today. Seems a little not instable.

![alt tag](img/2.png)

After unselect some resource in the first list the website still presents the unselected resource in the list. Could be confused for the user.

![alt tag](img/3.png)

Once the slice is reserved succefully, the color blue is not in the list (should be green?)

![alt tag](img/4.png)

After login no information about the projects. They disappeared. I did logout/login again to fix it. 

![alt tag](img/5.png)

Fail again in reserve the resources. (FIXED for now)

![alt tag](img/6.png)

After change to Paris resources, the screen never ends to load. Must reload the page and wait again for the left panel load. All the time it takes almost 2 minutes.

![alt tag](img/7.png)

Minor bugs.
Position of the text.

![alt tag](img/8.png)

Bug in messages.

![alt tag](img/9.png)

Unaccountable message. The user have no idea what means.

![alt tag](img/10.png)

When clicked in the list of resources, to see where is located the resource, for some reason the map and the logo did not appeared.

![alt tag](img/11.png)

In the case below, for the user does not matter to much this kind of lease message. Maybe for the tech people. The time is also incomprehensible. All the user wants here is know if the reservation is ok.
If by a mistake or not, you click in close, the window will disappear and the loading screen in background never ends to load something. To come back to the window you must apply again the reservation.
I have no idea if the close only close the window or if cancel all.

![alt tag](img/12.png)

The negative message when reserve a slice just told me: FAILURE. In fact it was because someone else already took the slice. Failure is a little generalist. If the site could say that the time is already taken I would know that is not a problem but a concurrent time.

Gerenal notes:
-There's no information about the adress to SSH access or clear message how to access the resource. Must rolled the portal in all directons to find only the Paris plataform address.

-The panel of schedule is complex, The number of options for the user is huge. In resource/slice reservation's screen the user has ~25 links to click... only in the main screen. In all this links the user can clicks: news, about, public website, intranet, onelablogo, experiment, support, users, information, tools, all available, unconfigured, pending, reserved, apply, table, map, scheduler, date slice table, previous & next, slice time icon, facilities itens.
-In the tabs, each one has new options and configurations.
-The button apply is in a confused position.

![alt tag](img/13.png)

Another example of complex screen for the users is the account tab in account option/slice reservation. I am little confused about all these credentials.

![alt tag](img/14.png)

The resource names have complex names. (ex.: host2.planetlab.informatik.tu-darmstadt.de)
I can login to faraday even my slice time ended.
I can load images even my slice time ended. My slice was until 15:30.

![alt tag](img/15.png)

