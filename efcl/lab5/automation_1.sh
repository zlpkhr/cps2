#!/bin/bash

is_int() {
    [[ "$1" =~ ^[0-9]+$ ]]
}

n=$1

if ! is_int "$n"; then
    echo "error: n is not int"
    exit 2
fi

op="$TMPDIR/$n.txt.utf-8"

curl -o "$op" -L "https://www.gutenberg.org/ebooks/$n.txt.utf-8"

title=$(grep '^Title:' "$op" | sed 's/Title: //')
title="${title// /_}"

sed -n '/START OF THE PROJECT GUTENBERG EBOOK/,/END OF THE PROJECT GUTENBERG EBOOK/p' "$op" | sed '1d;$d' > "$title.txt"

rm "$op"