# The R2Lab testbed

## Purpose

The R2Lab testbed, located at Inria Sophia Antipolis, and dedicated to **reproducible** wireless experiments, is open to public usage. See https://r2lab.inria.fr for details.

## Contents

This repo used to contain everything needed to run the testbed, but as it grew bigger and bigger miscellaneous pieces have been taken out and now sit in their own repo; this is the case for

* https://github.com/parmentelat/r2lab.inria.fr - contains the django app that runs on the testbed frontend

* https://github.com/parmentelat/r2lab-raw - contains some raw data such as various presentations and other snapshots

## Plans

* It is planned to also take out the `demos` subdir into a repo that will be called `r2lab-demos`

* Same possibly for the `infra` subdir, although it is not yet clear how it should be split into pieces.

## Todos

We are using [github issues on the main repo here](https://github.com/parmentelat/r2lab/issues) to track bugs and features requests and all other discussions about the testbed.
