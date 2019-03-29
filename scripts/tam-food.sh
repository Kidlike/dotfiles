#!/bin/bash

# Tamedia Food
# ./food <language>
# 
# language - (optional) list of languages: trans -R

set -eu

function checkDependency() {
    local cmd=${1:?Please provide dependency name to check}
    command -v "$cmd" >${STDWARN} 2>&1
    if [ $? -ne 0 ]; then
        echo "Required dependency not found: '$cmd'"
        exit
    fi
}

function setup() {
    DEBUG=${DEBUG:-0}
    if [ ${DEBUG} -ne 0 ]; then
        set -x
        STDWARN=/dev/stderr
    else
        STDWARN=/dev/null
    fi

    TMP_DIR=${TMP_DIR:-$(mktemp --directory)}
    trap _onExit EXIT

    if [ $# -eq 1 ]; then
        TO_LANG="$1"
    else
        TO_LANG="de"
    fi
}

function _onExit() {
    if [ $DEBUG == "0" ]; then
        rm -rf ${TMP_DIR}
    else
        echo ${TMP_DIR}
    fi
}

function _translate() {
    local xDe="$*"
    if [ "$TO_LANG" == "de" ]; then
        echo "$xDe"
    else
        local xEn=$(\trans -no-warn -e bing -b de:${TO_LANG} "$xDe")
        [ -n "$xEn" ] && echo "$xEn" || echo "$xDe"
    fi
}

function main() {
    cd ${TMP_DIR}
    \curl --silent --show-error --location --fail 'https://clients.eurest.ch/de/tamediazuerich/home' -o menu.html
    set +e
    \tidy --show-warnings no -quiet -numeric -asxhtml menu.html > menu-tidy.html 2>${STDWARN}
    if [ $? -ge 2 ]; then
        echo "Could not tidy the menu's html :("
        exit
    fi
    set -e
    \xq . menu-tidy.html > menu.json

    while read line; do
        local titleDe=$(echo $line | cut -d\@ -f1 | sed 's/^"//g')
        local descDe=$(echo $line | cut -d\@ -f2)
        local priceInt=$(echo $line | cut -d\@ -f3)
        local priceExt=$(echo $line | cut -d\@ -f4 | sed 's/"$//g')

        echo Title: $(_translate "$titleDe")
        echo Description: $(_translate "$descDe")
        echo Price Int: $priceInt
        echo Price Ext: $priceExt
        echo
    done< <(jq  '.. | select(."@class"?=="tab-content").div.div[] | .h3 + "@" + .p + "@" + .div.dl.dd[0] + "@" + .div.dl.dd[1]' menu.json | sed 's/\\n/ /g')
}

setup "$@"
checkDependency tidy
checkDependency xq
checkDependency jq
checkDependency trans
main

