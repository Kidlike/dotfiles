#!/bin/bash

for i in `ls *[0-9].vmdk`; do
	echo $i
	qemu-img convert -f vmdk $i -O raw ${i/vmdk/raw}
done

echo "cat raw to img"

cat *.raw >> system.img
