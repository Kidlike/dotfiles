#!/bin/bash

PID=$(pgrep gnome-session)
export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)

WALLS_PATH=/home/stefanos/Pictures/backgrounds/1920x1080
CUR_WALL=$(basename "$(gsettings get org.gnome.desktop.background picture-uri | cut -d\' -f 2)")

cd "${WALLS_PATH}"

if [ "$(ls -1 | tail -1)" == "${CUR_WALL}" ]; then
	NEW_WALL=$(ls -1 | head -1)
else
	NEW_WALL=$(ls -1 | grep -A1 "${CUR_WALL}" | tail -1)
fi

gsettings set org.gnome.desktop.background picture-uri "file://${WALLS_PATH}/${NEW_WALL}"

