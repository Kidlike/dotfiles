#!/bin/bash

kubectl get pods -o wide --all-namespaces | grep -E "lacework-agent-[a-z0-9]{5} " | while read -r line; do
    pod=$(echo $line | awk '{print $2}')
    node=$(echo $line | awk '{print $8}')

    nodeinfo=$(kubectl get node "$node" \
        -o jsonpath='{.metadata.labels.karpenter\.sh/nodepool}{"\t"}{.metadata.labels.eks\.amazonaws\.com/nodegroup}{"\t"}{.metadata.labels.node\.kubernetes\.io/instance-type}{"\t"}{.status.nodeInfo.architecture}{"\t"}{.status.capacity.cpu}{"\t"}{.status.capacity.memory}' \
      | awk -F'\t' '{
            pool = ($1 != "" ? $1 : $2)
            m = $6; sub(/Ki$/, "", m)               # memory comes as e.g. 4046672Ki
            printf "[%s | %s | %s, %s vCPU, %.0fGi]", pool, $3, $4, $5, m/1024/1024
        }')

    echo -e '\n---------'
    echo "$node $nodeinfo"
    echo '---------'

    kubectl debug -q -n lacework "${pod}" --attach --profile=general --image=public.ecr.aws/docker/library/busybox:latest --target=lacework -- \
    sh -c 'snap(){ for s in /proc/[0-9]*/stat; do awk "{print \$1\" \"\$12\" \"\$2}" "$s" 2>/dev/null; done; };
         snap > /tmp/a; sleep 15; snap > /tmp/b;
         awk "NR==FNR{a[\$1]=\$2;next} {d=\$2-a[\$1]; if(d>0) print d/15\" majflt/s \"\$3}" /tmp/a /tmp/b | sort -rn | head' </dev/null
done

