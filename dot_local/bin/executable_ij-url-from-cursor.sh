#!/bin/bash

copyToClipboards() {
  echo "$@" | \xclip -selection clipboard
  echo "$@" | \xclip
}

copyToClipboards "http://localhost:63342/api/file?file=$1&line=$2&column=$3"

