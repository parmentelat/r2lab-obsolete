title: Requirements for updating website
---

# markdown-styles

This is the software package that provides `generate-md` and its supported layouts

    sudo npm install -g markdown-styles

From what I can see this in turn requires `Node.js`, hence the usage of `npm`

# python3

This is required for `index.py` that enriches `index.md` with all known pages 

    sudo port install python34
    sudo port select --set python3 python34

# ssh access to webserver

For pushing stuff, you need to be allowed to run

    ssh root@r2lab.pl.sophia.inria.fr hostname

# See also

https://guides.github.com/features/mastering-markdown/
