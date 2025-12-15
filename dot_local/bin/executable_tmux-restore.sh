#!/bin/bash

if tmux list-sessions 2>/dev/null; then
    exec tmux attach-session
else
    exec tmux
fi

