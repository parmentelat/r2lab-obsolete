# expirations

* A linux account (so, a slice) created on R2lab has an expiration timeout
* This is not visible anywhere in the UIs (either at the portal or at r2lab's website)
* When this timeout triggers, the slice still shows up in the reservation widget, but will result in a request pending forever; django should try to show inspect the accounts and filter out invalid slices.
* Which probably is **also** a bug of its own in the UI

# How to fix

* one way to solve this situation should be to go to the portal and re-attach the node to the slice


# non-standard delegation

In my case, when trying to fix walid's slice, I had to

* add myself to the slice (because otherwise I would not see it)
* upload my credentials again so the delegated credential becomes available (which of course I totally forgot to do the first time)
* then go into the onelab portal, work my way to the UI that let's me renew slices - which I found not very obvious to find out..)


