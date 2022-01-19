#!/bin/bash

# shellcheck disable=SC2120
math-sum () {
    local nums=${*:-$(</dev/stdin)};
    echo $nums | tr ' ' '+' | bc
}

modules="auth
         breakingnews
         content
         editions
         external-content
         filerepo
         functions
         liveticker
         metadata
         notification
         placement
         releasenotes
         revisions
         rtelements
         search2
         slideshow
         tenant
         websocket
         webstats"
echo "$modules" | while read -r module; do
    echo "> $module"

    wd=$(pwd)
    cd "$module" || exit 1

    deps=$(mvn -DignoreUnusedRuntime -DignoreNonCompile dependency:analyze -Pdirty | grep -A 1000 'Unused declared dependencies found:' | grep WARNING | sed '1d' | awk '{print $2}')
    totalClassCount=0
    totalSizeCount=0
    while read -r d; do
        groupId=$(echo "$d" | cut -d: -f1 | tr . /)
        artifactId=$(echo "$d" | cut -d: -f2)
        type=$(echo "$d" | cut -d: -f3)
        version=$(echo "$d" | cut -d: -f4)

        jarFile=$(find "$HOME/.m2/repository/$groupId/$artifactId/$version/" -name "*.$type" -printf '%s %p\n' | sort | head -1 | awk '{print $2}')
        jarSize=$(stat --print='%s' "$jarFile")
        totalSizeCount=$((totalSizeCount + jarSize))

        td=$(mktemp -d)
        cd "$td" || exit 1
        cp "$jarFile" .
        unzip -q -- *
        classCount=$(find . -type f -name '*.class' | wc -l)
        totalClassCount=$((totalClassCount + classCount))

        cd - >/dev/null || exit 1
        rm -rf "$td" || exit 1
    done < <(echo "$deps")

    echo "unused dependencies: $(echo "$deps" | wc -l)"
    echo "total size: $(echo "scale=2; $totalSizeCount / 1024 / 1024" | bc) MB"
    echo "total class count: $totalClassCount"
    echo

    cd "$wd" || exit 1
done
