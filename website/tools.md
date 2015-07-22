title: Tools
tab: platform
---

### NEPI: Network Experiment Programming Interface

NEPI is a Python-based library to model and run network experiments on a variety of network evaluation platforms, including PlanetLab, OMF wireless testbeds, ns-3 simulators, and others. It allows to specify resources to use in an experiment, to define experiment workflow constraints and to automate deployment, resource control and result collection.

#####Features :
- Automatic experiment deployment
- Automatic result collection
- Interactive expermentation
- Hybrid experiments with multiple platforms
- Free open source license (GPLv2)

#####Instalation:
    $ sudo pip install nepi

This will take care of the ipaddr and networkx dependencies.

#####Update:
Within this framework, you can update to the latest stable version of NEPI by simply running:
    
    $ sudo pip update nepi

#####Visualizing:
If you also need functions related to matplotlib and pygraphviz, you can have the python code for these two tools installed using an explicit.

    $ sudo pip install matplotlib pygraphviz

However, please be aware that for this command to succeed, you will need to have the corresponding C libraries installed first by another method ([see details](http://nepi.inria.fr/Install/WebHome)).

#####Experiments with NEPI:

- [How to design an experiment using NEPi](http://nepi.inria.fr/Nepi/StepByStepExperiment)
- [How to deploy an experiment using NEPi](http://nepi.inria.fr/Nepi/StepByStepExperiment)
- [Ping example using NEPI](http://nepi.inria.fr/code/nepi/file/a94139d39d2e/examples/linux/ping.py)