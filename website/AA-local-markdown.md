# OBSOLETE

This file is now obsolete, as the change in question has made it
upstream as part of markdown-styles v3.0.0

# How to use our own `markdown-styles`

We have proposed a patch to upstream's `markdown-styles` so that `meta.json` can be used to implement cascading scope of metavariables based on the input source filenames

[See this link for more details on the feature](https://github.com/parmentelat/markdown-styles/commit/551e344fdabc7a66dcf1e78fb30d15b37d2f2b55)

## forked as parmentelat

I have forked [the upstream git repo (mixu)](https://github.com/mixu/markdown-styles) as [`parmentelat` in github](https://github.com/parmentelat/markdown-styles)

This fork is expected to have been git-cloned at the same level as `r2lab`; that is to say, in my case I have

  * `~/git/r2lab`
  * `~/git/markdown-styles`
    
This latter one being cloned from

    https://github.com/parmentelat/markdown-styles.git

* It is still required to use `npm` to install upstream `markdown-styles` so that other dependencies are installed as well.

## Usage

With all this in place it should be possible to run

	cd website
	make convert-local

or

	cd website
	make preview-local
	
to use our version of `markdown-styles`; which essentially does this:

    export NODE_PATH=$HOME/git/markdown-styles/lib:/usr/local//lib/node_modules/markdown-styles/node_modules
    ../../markdown-styles/bin/generate-md --layout ./r2lab-layout --input markdown --output html
