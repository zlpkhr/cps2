#!/usr/bin/env bash

pdf_file=$1
question=$2

if [ "$pdf_file" == "" ]; then
    echo "<pdf_file> is required."
    exit 1
fi

if [ "$question" == "" ]; then
    echo "<question> is required."
    exit 1
fi

if [ "$(file --mime-type -b "$pdf_file")" != "application/pdf" ]; then
    echo "<pdf_file> must be a PDF file."
    exit 1
fi

pdftotext "$pdf_file" "$TMPDIR/$pdf_file"
pdf_text=$(cat "$TMPDIR/$pdf_file")

data=$(jq -n \
    --arg model "gemma:2b" \
    --arg prompt "You are a PDF assistant. Your job is to answer the following question: $question, based only on the following content from the PDF file: $pdf_text" \
    --argjson stream false \
    '{model: $model, prompt: $prompt, stream: $stream}')

curl -s http://localhost:11434/api/generate -d "$data" | jq ".response"
