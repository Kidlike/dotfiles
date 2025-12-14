#!/bin/bash

set -x

SCRIPT="certificate-permanently-accept"
DOT=".${SCRIPT}"

usage() {
    echo "${SCRIPT} <HOSTNAME> <PORT> <NICKNAME>"
}

if [ $# -ne 3 ]; then
    usage
    exit 1
fi

hostname="$1"
port="$2"
nickname="$3"
certFile="${hostname}-${port}--${nickname}.cert"

cd "${HOME}"
mkdir "${DOT}" 2>/dev/null
cd "${DOT}"

gnutls-cli --print-cert -p ${port} ${hostname} < /dev/null | \
awk '/-----BEGIN CERTIFICATE-----/{f=1} /-----END CERTIFICATE-----/{f=0;print} f' \
> "${certFile}"

certutil -d "sql:${HOME}/.pki/nssdb" -A -t P -n "${nickname}" -i "${certFile}"
