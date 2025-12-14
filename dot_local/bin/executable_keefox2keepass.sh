#!/bin/bash

function ensureFile() {
	if [ ! -r $1 ]; then
		echo "Could not find $2"
		exit 1
	fi
}

keefoxPlugin="$(find ~/.mozilla/firefox/ -type d -name 'keefox@*')/deps/KeePassRPC.plgx"
ensureFile $keefoxPlugin "keepass plugin for keefox"

keepassHome=$(whereis keepass2 | tr ' ' '\n' | grep "lib/keepass")
if [ ! -r $keepassHome ]; then
	sudo updatedb
	keepassHome=$(locate lib/keepass | egrep -v "lib/keepass.?[/]+")
fi
ensureFile $keepassHome "plugin directory for keepass"
keepassPlugins="${keepassHome}/plugins"

if [ ! -w "$keepassHome" ]; then
	SD="sudo"
fi

$SD mkdir "$keepassPlugins" 2>/dev/null
$SD cp -f "$keefoxPlugin" "$keepassPlugins"
ret=$?

if [ $ret -eq 0 ]; then
	echo "Done!"
	echo "Restart KeePass and Firefox"
else
	echo "Something went wrong"
	exit $ret
fi
