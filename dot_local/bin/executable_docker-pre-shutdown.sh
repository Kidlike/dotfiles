#!/bin/bash

docker service ls --format '{{.Name}}'  | xargs -r -I{} docker service scale --detach=true {}=0

