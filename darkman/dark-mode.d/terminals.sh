#!/bin/bash

# https://gogh-co.github.io/Gogh/

qdbus org.kde.yakuake /Sessions/1 setProfile "Wombat"

KONSOLEPIDS=($(pidof konsole))
for i in "${KONSOLEPIDS[@]}"; do
    # get number of sessions this particular instance has
    CURRENTSESSIONCOUNT=$(qdbus org.kde.konsole-$i /Windows/1 sessionCount)
    for x in $(seq 1 $CURRENTSESSIONCOUNT); do
        # change profile through dbus message
        qdbus org.kde.konsole-$i /Sessions/$x setProfile "Wombat"
    done
done

