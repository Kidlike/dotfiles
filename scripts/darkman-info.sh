#!/bin/bash

if [[ $(gsettings get org.gnome.desktop.interface gtk-theme) =~ "Nordic-darker" ]]; then
  echo '🕶️'
else
  echo '👓'
fi
