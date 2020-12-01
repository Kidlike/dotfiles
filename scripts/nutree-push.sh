#!/usr/bin/env bash

git branch -vv | grep -E '^\*' | grep -oE '\[([^/]+)\/[^]]+\]'
# TODO
