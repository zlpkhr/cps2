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

wc=$(wc -w < "$title.txt" | xargs)
sc=$(grep -o '[.!?]' "$title.txt" | wc -l | xargs)

echo "words: $wc"
echo "sentences: $sc"

tr -d '[:punct:][:digit:]' < "$title.txt" | tr '[:upper:]' '[:lower:]' | tr -s ' ' '\n' | grep -v '^[[:space:]]*$' > "$TMPDIR/$title.txt.tr"
sort < "$TMPDIR/$title.txt.tr" | uniq -c | sort -nr > "$title.txt.histogram"                                                          

rm "$op"
rm "$TMPDIR/$title.txt.tr"