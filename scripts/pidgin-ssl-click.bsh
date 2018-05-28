#!/bin/bash

current_mouse_info=$(xdotool getmouselocation --shell)
restore_mouse_x=$(echo "$current_mouse_info" | grep "X=" | cut -d\= -f2)
restore_mouse_y=$(echo "$current_mouse_info" | grep "Y=" | cut -d\= -f2)

xdotool search "SSL Certificate Verification" windowactivate --sync
window_info=$(xwininfo -id $(xdotool getactivewindow))
window_w=$(echo "$window_info" | egrep "[ \t]+Width:" | cut -d\: -f2 | cut -d\  -f2)
window_h=$(echo "$window_info" | egrep "[ \t]+Height:" | cut -d\: -f2 | cut -d\  -f2)
goto_x=$(echo "$window_w - 80" | bc)
goto_y=$(echo "$window_h - 30" | bc)

xdotool search "SSL Certificate Verification" windowactivate --sync mousemove --sync --window %@ $goto_x $goto_y click 1 mousemove $restore_mouse_x $restore_mouse_y
