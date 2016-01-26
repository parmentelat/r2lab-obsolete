# Dependencies

In order to write this authentication module, we have 2 dependencies towards

* `manifold` from the `manifold` project
* `manifoldapi` from the `myslice` project

## setup

So as of this writing, here is what I did on my devel box

```
(py3-dj1.9)parmentelat ~/git/r2lab/r2lab.inria.fr $ pwd
/Users/parmentelat/git/r2lab/r2lab.inria.fr
(py3-dj1.9)parmentelat ~/git/r2lab/r2lab.inria.fr $ ln -s ~/git/manifold/manifold
(py3-dj1.9)parmentelat ~/git/r2lab/r2lab.inria.fr $ ln -s ~/git/myslice/manifoldapi/
```

## git revisions 

```
(py3-dj1.9)parmentelat ~/git/r2lab/r2lab.inria.fr $ for i in manifold manifoldapi; do (cd $i; git log HEAD^..HEAD) ; done
commit 97b5f93bb5e1322253d24586efc67fc8a5b6106b
Author: Thierry Parmentelat <thierry.parmentelat@inria.fr>
Date:   Mon Jan 25 14:18:02 2016 +0100

    partially compatible with python3
    changes were on a need-by-need basis so that myslice/manifoldapi
    can be used under python3
commit 9a3a3f6f897541374fb7e14dece6fb464c3fa48f
Author: Thierry Parmentelat <thierry.parmentelat@inria.fr>
Date:   Tue Jan 26 16:35:04 2016 +0100

    an import actually was relative; make it qualified with manifoldapi.
```

## micro tester

Which led me to this

```
mfauth $ mfbackend.py
validate: demo / demo : authenticated OK
ERROR:root:GetSession failed: None
validate: NOPE with demo / not-the-password : authenticated OK
```

## NOTES

I tried to have a symlink `myslice` instead of `manifoldapi` so I would have been able to import `unplug` as well. It was not working, `myslice/` does not have a `__init__.py`.

Besides I'm not sure if this django-1.5 code would have been usable anyway