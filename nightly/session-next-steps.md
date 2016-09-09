# Intro

This memo aims at summarizing my comments on `session.py` and where we should go with it.

# Overview

All in all I like the idea a lot, and believe it could be quite helpful for deploying real experiments

# Next steps

IMHO, here's a non-exhaustive list of angles for improvement

## **integrate in `rhubarbe`**

I'm still not sure about using either `snap` or `snapshot` or `testbed` as the keyword here, but assuming it's `snap` as it's the shortest, we could have an interface like this:

* First off, an alias `rsnap` and/or just `snap` that does `rhubarbe snap`

* Let us emphasize at this point that embedding this into `rhubarbe` wouldd also means optimal performance, in using the native classes instead of forking various instances of `rhubarbe-load` or similar as external processes, especially in terms of parallelization.

* Each snapshot must be created in an isolated json file, like `.snap`. This way we can use regular Unix commands to move, rename and delete stuff around; or promote one snapshot from user-local to publicly available - much like we do for images.

* The supported interface could then be something like

```
rhubarbe snap --save|-s snapname
rhubarbe snap --load|-l snapname
rhubarbe snap --view|-v snapname
```

* In the above, one could indifferently refer to `snapname` or `snapname.snap`, so that one can use bash completion.

* Finally, as I mentioned already, it is crucial that `snap --save` is to leverage on `/etc/rhubarbe-image` for elaborating the snapshot. It will make things at the same time simpler to code, more efficient, and more accurate.

## node selection

In terms of node selection, several angles can be taken

### (A) Always save the whole testbed

In this simplest mode, saving would create a full dictionary of items of the form

```
hostname -> (on_or_off, image_name)
```

Or some other equivalent data. ***XXX*** In particular, if a node is off, we can always retrieve the last image installed through sidecar, but this might be brittle/unreliable; not even sure it is useful at all.

Anyways, in this mode a snapshot would always remember the complete status of the testbed.
From that point we can image 2 submodes:

1. Restoring (loading) would always put the testbed exactly like it was
1. or we add options to the `--save` feature so that some nodes can be left as they are

I like the first option in fact, because it's simple and thus immune to errors; but at the same time I am also sure that we will occasionally face situations where this is an impediment.

### (B) Allow users to restrict saving to a specific set of nodes

In this mode, a session would contain information only about a subset. We can here again consider 2 submodes, that would respectively

1. Restore all the nodes as described in the snapshot,
1. or allow for exclusions

It's my feeling that both options B.1 and B.2 make the whole business uselessly cumbersome and error-prone, so I would rather go for B.1 as a first target, and possibly move to B.2 if it turns out to be too much of a hindrance.

## Miscell

* At first sight I would think that this feature is totally oblivious to notions like 'preferred' images, and that it does not need to use any list of VERSIONS at all. I'm not even sure it needs to know about the location for the images repository.

* ~~On a more detailed level, the creation of `parser` and `args` and similar should be done **inside the `main` function** and not at the module toplevel. This way testers can be connected to `__main__` when integrated in `rhubarbe`. This applies to coding in python in general, and so BTW it's the same for `book-nightly.py`~~.

* ~~in `check_status`, the incoming `silent` variable should be a `bool`, not a string, as far as possible~~

* ~~in `show_examples`, please use triple quotes `'''` instead of adding newlines manually with `\n` all over the place~~

* I Just made a few cosmetic changes to the code, please reveiew and apply these wherever applicable.


## Comments

Feel free to modify the text directly since git will let us follow easily, or to just add your comments in the bulletted list below, just please use a similar format

* ***From Mario Z. - 9 Sept.*** : refactoring code for parser args and the suggested minor changes.
* ***From Mario Z. - 8 Sept.*** : check_status, show_examples and book-nightly suffered the minor changes. The adopted name is now **snapshot** with future `snap` and `rsnap` as alias.
* ***From Thierry P. - 7 Sept.*** : a dummy formatted comment
