#!/bin/bash

is_int() {
    [[ "$1" =~ ^[0-9]+$ ]]
}

if [ $# -eq 0 ]; then
    for i in {1..10}; do
        echo "$i"
    done

    ec=1
elif [ $# -eq 1 ]; then
    if ! is_int "$1"; then
        echo "error: min is not int"
        exit 2
    fi

    for ((i = 1; i <= $1; i++)); do
        echo "$i"
    done

    ec=0
elif [ $# -eq 2 ]; then
    if ! is_int "$1"; then
        echo "error: min is not int"
        exit 2
    fi

    if ! is_int "$2"; then
        echo "error: max is not int"
        exit 2
    fi

    if [ "$1" -ge "$2" ]; then
        echo "error: min > max"
        exit 2
    fi

    for ((i = $1; i <= $2; i++)); do
        echo "$i"
    done
    
    ec=0
fi

exit $ec