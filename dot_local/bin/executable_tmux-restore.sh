#!/bin/bash

while true; do
    if tmux list-sessions 2>/dev/null; then
        tmux attach-session
    else
        tmux
    fi
done
