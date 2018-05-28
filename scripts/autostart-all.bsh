#!/bin/bash

function log() {
	echo "$(date +[%H:%M.%S]) $@" | tee -a ~/var/log/autostart-all.log
}

LOCKFILE="/var/lock/`basename $0`"
LOCKFD=99

# PRIVATE
_lock()             { flock -$1 $LOCKFD; }
_no_more_locking()  { _lock u; _lock xn && rm -f $LOCKFILE; }
_prepare_locking()  { eval "exec $LOCKFD>\"$LOCKFILE\""; trap _no_more_locking EXIT; }

# ON START
_prepare_locking

# PUBLIC
exlock_now()        { _lock xn; }  # obtain an exclusive lock immediately or fail
exlock()            { _lock x; }   # obtain an exclusive lock
shlock()            { _lock s; }   # obtain a shared lock
unlock()            { _lock u; }   # drop a lock

# run only once
exlock_now || exit 1

### BEGIN OF SCRIPT ###
log "autostart-all begins"

# Wait for unity
log "waiting for unity..."
ret=$(ps -ef | grep unity-panel-service | grep -v grep | wc -l)
while [ "$ret" == "0" ]; do
	ret=$(ps -ef | grep unity-panel-service | grep -v grep | wc -l)
	sleep 1
done
log "unity started"


# No internet required section start
log "========= NO INTERNET REQUIRED =========="


# Clipboard Manager
clipit &
disown
log "clipit started"


# Backup skype user folder (there's a rare bug that skype looses it's configuration)
if [ $(ls -1 ~/backups/skype-settings-backup | wc -l) -ge 7 ]; then
	rm -rf ~/backups/skype-settings-backup/$(ls -1tr ~/backups/skype-settings-backup | tail -1) &
fi
if [ ! -e ~/backups/skype-settings-backup/$(date +%Y%m%d) ]; then
	mkdir -p ~/backups/skype-settings-backup/$(date +%Y%m%d)
	cd ~/backups/skype-settings-backup/$(ls -1tr ~/backups/skype-settings-backup | tail -1)
	tar -czpf user-folder-backup.tar.gz ~/.Skype/ &
fi
log "skype folder backed up"


# lightsOn (disable sleep when fullscren)
lightsOn &
disown
log "lightsOn started"


# indicator-messaging-numlock-notify
#lock-unlock-wrapper = ~/install/_scripts/indicator-messaging-numlock-notify.bsh = "/usr/local/bin/killgrep -9 indicator-messaging-numlock-notify.bsh; /usr/local/bin/killgrep numlock-blink; /usr/local/bin/killgrep -9 com.canonical.indicator.messages" >/dev/null 2>&1 &

# autokeyZ
autokey-gtk &
disown
log "autokey-gtk started"

# No internet required section end


log "========= INTERNET REQUIRED =========="

# Wait for internet
log "waiting for internet..."
host=www.google.com
curl --connect-timeout 10 -s $host
ret=$?
while [ ! "$ret" == "0" ]; do
	curl --connect-timeout 10 -s $host
	ret=$?
done
log "internet !"


# sparkleshare
sparkleshare start &
disown
log "sparkleshare started"


# Thunderbird start
pgrep thunderbird
ret=$?
if [ ! "$ret" == "0" ]; then
	/usr/bin/thunderbird &
	disown
fi

# Search for Thunderbird window
TB=$(xdotool search --class thunderbird)
while [ -z "$TB" ]; do
	sleep 1
	TB=$(xdotool search --class thunderbird)
done

# dispose Thunderbird window
while [ true ]; do
	if [ "$(xdotool search --class thunderbird getwindowgeometry | grep -i geometry | cut -d\: -f2 | tr -d ' ')" == "10x10" ]; then
		sleep 1
		# xdotool search --class thunderbird focus %@
		xdotool search --class thunderbird windowunmap %@
	else
		break
	fi
done
# Thunderbird end
log "thunderbird started"

# Redshift
redshift-gtk &
disown
log "redshift started"

# Weather Indicator
/opt/extras.ubuntu.com/my-weather-indicator/bin/my-weather-indicator &
disown
log "weather indicator started"


# StackApplet
/usr/share/stackapplet/stackapplet.py &
disown
log "stackaplet started (stackoverflow)"


# fix ExpoEdge...
gconftool --set --type string /apps/compiz-1/plugins/expo/screen0/options/expo_edge ""
sleep 0.5
gconftool --set --type string /apps/compiz-1/plugins/expo/screen0/options/expo_edge "TopRight"

exit 0
