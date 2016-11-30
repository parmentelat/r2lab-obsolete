#!/bin/bash
function foo () {
    echo "in function foo"
    for arg in "$@"; do echo "foo arg: " $arg; done
}
    
function bar () {
    echo "in function bar"
    for arg in "$@"; do echo "bar arg: " $arg; done
}

"$@"
