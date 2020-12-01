#!/bin/bash

sudo modprobe nfs
sudo modprobe nfsd
docker run -v /tmp/nfs-data:/cdm -v ~/exports.txt:/etc/exports:ro --cap-add SYS_ADMIN -p 2049:2049 erichough/nfs-server
