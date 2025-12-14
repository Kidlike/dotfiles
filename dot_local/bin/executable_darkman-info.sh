#!/bin/bash

if [[ $(gsettings get org.gnome.desktop.interface gtk-theme) =~ "Aritim-Dark-GTK" ]]; then
  echo '🕶️'
else
  echo '👓'
fi
