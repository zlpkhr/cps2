#!/bin/bash

echo "params.length=$#"

if [ $# -gt 0 ]; then
    i=0
    for p in "$@"; do
        echo "params[$i]=$p"
        ((i++))
    done
fi