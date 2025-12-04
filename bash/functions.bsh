#!/bin/bash

function help-curl-data() {
  echo '--data @<(cat <<EOF'
  echo '_payload_'
  echo 'EOF'
  echo ')'
}

function pwd-physical() {
  logical=$(builtin pwd -L)
  physical=$(builtin pwd -P)

  if [ "${logical}" == "${physical}" ]; then
    echo "${logical}"
  else
    echo "${logical} -> ${physical}"
  fi
}

function whatismyip() {
  curl ipv4.icanhazip.com
}

function pdfman() {
  if [ ! -r /tmp/pdfman-$1.pdf ]; then
    man -t $1 | ps2pdf - /tmp/pdfman-$1.pdf
  fi
  evince /tmp/pdfman-$1.pdf
}
complete -F _man pdfman

function killprocname() {
  procs=`ps -ef | grep -i "$1" | grep -v grep | tr -s " " " " | cut -d\  -f 2`

  oldIFS=IFS
  IFS=\
    countProcs=`echo $procs | wc -l`
      IFS=$oldIFS

      if [ ${countProcs} -gt 1 ]
      then
	echo "Not unique selection..." &> /dev/stderr
	return
      elif [ "$(echo $procs)X" == "X" ]
      then
	echo "No such process..."
	return
      fi
      echo "kill: ${procs}"
      kill -9 ${procs}
    }

  function grepkill() {
    if [ $# -eq 1 ]; then
      killargs="-9"
      filter=$1
    elif [ $# -eq 2 ]; then
      killargs=$1
      filter=$2
    fi
    procs=`ps -ef | grep -i "$filter" | grep -v grep | tr -s " " " " | cut -d\  -f 2`
    if [ ! -z "${procs}" ]; then
      kill ${killargs} ${procs}
    else
      echo "no processes found";
    fi
  }

function mvn-debug() {
  mvn -Dmaven.surefire.debug="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=8000" "$@"
}

function mvn-go-up() {
  while ! ls pom.xml >/dev/null 2>&1; do
    [ "$(pwd)" == ~ ] && break;
    cd ..
  done
}

function git-go-up() {
  while ! ls .git/ >/dev/null 2>&1; do
    [[ "$(pwd)" == ~ || "$(pwd)" == "/" ]] && break;
    cd ..
  done
}

if command -v svn >/dev/null 2>&1; then
  function svn-go-up() {
    while ! ls .svn >/dev/null 2>&1; do
      [ "$(pwd)" == ~ ] && break;
      cd ..
    done
  }
fi

function cd-switch() {
  cd $(pwd | sed "s#/$1/#/$2/#g")
}

function load-scripts() {
  if [ -d ~/.dotfiles/scripts ]; then
    mkdir -p ~/.local/bin 2>/dev/null
    cd ~/.dotfiles/scripts
    for f in $(\ls -1); do
      linkName=$(echo $f | rev | cut -d\. -f2- | rev)
      rm -f ~/.local/bin/$linkName 2>/dev/null
      if [ -x $f ]; then
	ln -sf ~/.dotfiles/scripts/$f ~/.local/bin/$linkName
      fi
    done
    cd - >/dev/null 2>&1
  fi
}

function unload-scripts() {
  if [ -d ~/.dotfiles/scripts ]; then
    cd ~/.dotfiles/scripts
    for f in $(\ls -1); do
      linkName=$(echo $f | rev | cut -d\. -f2- | rev)
      rm -f ~/.local/bin/$linkName 2>/dev/null
    done
    cd - >/dev/null 2>&1
  fi
}

if command -v homesick >/dev/null 2>&1; then
  function homesick-all() {
    [ $# -ne 1 ] && homesick && return 1;
    [ $(homesick | tr -s ' ' ' ' | grep -B1000 "options:" | cut -d\  -f 3 | egrep "^[a-zA-Z]+$" | egrep -c "^${1}$") -ne 1 ] && echo "Invalid command" && return 2;
    while read hl; do
      repo=$(echo $hl | tr -s ' ' ' ' | cut -d\  -f1);
      #echo -e "\e[31m--= ${repo} =--\e[39m"
      echo -e "\e[43m--= ${repo} =--\e[39m\e[49m"
      homesick $1 $repo;
      echo
    done < <(homesick list )
  }
fi

function free-swap() {
  free_data="$(free)"
  mem_data="$(echo "$free_data" | grep 'Mem:')"
  free_mem="$(echo "$mem_data" | awk '{print $4}')"
  buffers="$(echo "$mem_data" | awk '{print $6}')"
  cache="$(echo "$mem_data" | awk '{print $7}')"
  total_free=$((free_mem + buffers + cache))
  used_swap="$(echo "$free_data" | grep 'Swap:' | awk '{print $3}')"

  echo -e "Free memory:\t$total_free kB ($((total_free / 1024)) MB)\nUsed swap:\t$used_swap kB ($((used_swap / 1024)) MB)"
  if [[ $used_swap -eq 0 ]]; then
    echo "Congratulations! No swap is in use."
  elif [[ $used_swap -lt $total_free ]]; then
    echo "Freeing swap..."
    sudo swapoff -a
    sudo swapon -a
  else
    echo "Not enough free memory. Exiting."
    return 1
  fi
}

#if [ $(lsb_release -d | grep -ic ubuntu) -ge 1 ]; then
#	function delete-old-kernels() {
#		sudo apt-get purge $(dpkg -l linux-{image,headers}-"[0-9]*" | awk '/ii/{print $2}' | grep -ve "$(uname -r | sed -r 's/-[a-z]+//')")
#	}
#fi

function pitest-results() {
  lastReport=$(\ls -1trh target/pit-reports/ | tail -1)
  xdg-open $(pwd)/target/pit-reports/${lastReport} >/dev/null 2>&1
}

function lllast() {
  find $@ -maxdepth 1 -type f | xargs ls -ltr 2>/dev/null | tail -1
}

function tmux-mvn-rename() {
  tmux rename-window -t $(tmux display-message -p '#I') "$(xmlstarlet sel -N x='http://maven.apache.org/POM/4.0.0' -t -v '/x:project/x:name' pom.xml)"
}

function notify-speaker() {
  ( \speaker-test --frequency $1 --test sine )&
  pid=$!
  \usleep $((${2}*1000))
  exec 3>&2          # 3 is now a copy of 2
  exec 2> /dev/null  # 2 now points to /dev/null
  \kill -9 $pid >/dev/null 2>&1
  usleep 1000
  exec 2>&3          # restore stderr to saved
  exec 3>&-          # close saved version
}

function notify-speaker-command-done() {
  #notify-speaker 432 400 &>/dev/null
  notify-speaker 2160 150 &>/dev/null
  usleep 150000
  notify-speaker 2160 150 &>/dev/null
}

function pastebin() {
  if [[ $1 ]]; then
    curl -F 'sprunge=<-' "http://sprunge.us" <"$1"
  else
    curl -F 'sprunge=<-' "http://sprunge.us"
  fi
}


if [ -n $TMUX ]; then
  function ssh() {
    /usr/bin/ssh $@
    pid=$!
    if [ -r ~/.ssh/.sessions/$pid ]; then
      tmux rename-window "$(cat ~/.ssh/.sessions/$pid)"
      tmux setw automatic-rename on
      rm ~/.ssh/.sessions/$pid >/dev/null 2>&1
    fi
  }
fi

MVN() {
  $MVN $@
}

function mvn-jq-profile-deployables() {
  local profileId=$1
  shift
  jq ".project.profiles.profile | map(select(.id==\"${profileId}\")) | .[] .build .plugins .plugin | map(select(.artifactId==\"cargo-maven2-plugin\")) | .[] .configuration .configuration .deployables .deployable" "$*"
}

function kill-tomcat() {
  pid=$(pgrep -f 'java .*/opt/tomcat')
  rc=$?
  if [ $rc -ne 0 ]; then
    pid=$(pgrep -f 'java .*/opt/fc-apache-tomcat')
    rc=$?
    [ $rc -ne 0 ] && return $rc;
    kill -9 $pid
  else
    kill -9 $pid
  fi
}

function kill-sky() {
  kill -9 $(pgrep -f '/usr/lib/sky') 2>/dev/null
  kill -9 $(pgrep -f 'sky-latest-x86_64') 2>/dev/null
}

function mvn-generate-master-password() {
  if [[ ! -e ~/.m2/settings-security.xml ]]; then
    PASSWORD_ENCODED=$(mvn -emp "$(cat /dev/urandom|base64|head -n1)" );
    cat > ~/.m2/settings-security.xml  <<EOF
<settingsSecurity>
  <master>${PASSWORD_ENCODED}</master>
</settingsSecurity>
EOF

echo Created '~/.m2/settings-security.xml';
fi
}

function mvn-encrypt-passwd() {
  if [ ! -r ~/.m2/settings-security.xml ]; then
    mvn-generate-master-password
  fi
  read -p "Please enter your password: " -s PASSWORD
  local ENCRYPTED="$(mvn -ep ${PASSWORD})"
  echo
  echo "Your encrypted password is: ${ENCRYPTED}"
}

function mvn-set-passwd() {
  mvn-generate-master-password;
  echo Please enter your Windows/Network password. This will replace ALL server passwords in your '~/.m2/settings.xml' file.;
  echo -n "> ";
  read -s PASSWORD;
  PASSWORD="$(mvn -ep ${PASSWORD})";
  echo;
  echo Encrypted password is ${PASSWORD};
  cd ~/.m2;
  cp settings.xml settings.xml.old;
  xml2json -t xml2json --pretty --strip_newlines --strip_namespace --strip_text settings.xml > settings.json.old
  jq ".settings.servers.server[].password = \"${PASSWORD}\"" settings.json.old > settings.json
  xml2json -t json2xml settings.json | xmllint --format - > settings.xml
  echo 'Updated in ~/.m2/settings.xml';
  cd - > /dev/null 2>&1
}

function mvn-tomcat-deploy() {
  module=$(xmlstarlet sel -N x='http://maven.apache.org/POM/4.0.0' -t -v '/x:project/x:artifactId' pom.xml)
  war=$(find target/${module}-*.war)
  if [ ! -r "$war" ]; then
    echo "Did you build first?"
    return
  fi
  cp "$war" "/opt/tomcat/webapps/${module}.war"
  sync
}

function find-type() {
  type=$1
  shift
  find . -type f -name "*.$type" "$@"
}

function find-types() {
  while read ext; do
    count=$(find . -type f -iname "*\.$ext" | wc -l)
    echo -e "$ext\t$count"
  done< <(find . -type f -regex '.*src\/.*\..*$' | awk -F '.' '{print $NF}' | sort -u) |
    column -t -x |
    sort -rn -k2
  }

function svn-checkout-uat-sp12() {
  svn co --depth files "$1" uat
  svn update --depth files uat/automatic
  svn update uat/automatic/uat_services
}

function svn-checkout-uat-sp18() {
  svn co --depth files "$1" uat
  svn update --depth files uat/automatic
  svn update uat/automatic/uat
  svn update uat/automatic/src
  svn update uat/automatic/logs
}

function mvn-cleanup-old-artifacts() {
  oldRemaining=$(df -Ph ~/.m2/repository/ | tail -1 | awk '{print $4}')
  all=$(find ~/.m2 -type d -name "*SNAPSHOT" | wc -l)
  del=$(find ~/.m2 -type d -mtime +90 -name "*SNAPSHOT" | wc -l)
  find ~/.m2 -type d -mtime +90 -name "*SNAPSHOT" -exec rm -rf {} \; 2>/dev/null
  newRemaining=$(df -Ph ~/.m2/repository/ | tail -1 | awk '{print $4}')
  percentage=$(echo 100*${del}/${all} | bc)
  echo -n "Cleaned up ${percentage}%."
  [ $percentage -gt 0 ] && echo -n " Free space: ${oldRemaining} -> ${newRemaining}"
  echo
}

function intellij-cleanup() {
  if [ -d '.idea' ]; then
    rm -rf '.idea'
    find . -type f -name '*.iml' -delete
    echo "Cleaned up IntelliJ files."
  else
    echo "No IntelliJ project found."
  fi
}

function svn-ignore-intellij-files() {
  while read f; do
    dir=$(echo $f | rev | cut -d\/ -f2- | rev);
    props="$(svn propget svn:ignore $dir)"
    props=$(echo "$props" | grep -v 'iml')
    props=$(echo "$props
    *.iml")
    svn propset svn:ignore "$props" "$dir";
  done < <(find . -type f -name '*.iml')
}


function svn-ignore-maven-target() {
  while read d; do
    dir=$(echo $d | rev | cut -d\/ -f2- | rev);
    props="$(svn propget svn:ignore $dir)"
    props=$(echo "$props" | grep -v 'target')
    props=$(echo "$props
    target")
    svn propset svn:ignore "$props" "$dir";
  done < <(find . -type d -name 'target')
}

function kube-ns() {
  local NS=$1
  if [ -z "$NS" ]; then
    local NS=$(grep -i namespace ~/.kube/config | awk "{print \$2}")
  else
    kubectl config set-context $(kubectl config current-context) --namespace=$NS
  fi
  export KUBE_NS="$NS"
}

function git-branch-prune() {
  git fetch -p
  for branch in `git branch -vv | grep ': gone]' | awk '{print $1}'`; do 
    git branch -D $branch
  done
}

function git-branch-report() {
  local hasConflicts
  echo 'branch name,commits from master,has merge conflicts'
  git branch --remotes | grep -v master | while read -r b; do 
    git merge --no-commit --no-ff $b >/dev/null 2>&1
    hasConflicts=$?
    git merge --abort >/dev/null 2>&1
    echo $b,$(git rev-list --count $b..origin/master),$hasConflicts; 
  done
}

function treel() {
  tree -C "$@" | less -R
}

function mvn-surefire-report() {
  echo ">> Generating report..."
  mvn surefire-report:report-only "$@" >/dev/null
  mvn site -DgenerateReports=false "$@" >/dev/null

  echo ">> Opening report..."
  xdg-open target/site/surefire-report.html >/dev/null 2>&1
}

function jacoco-results() {
  xdg-open target/site/jacoco/index.html >/dev/null 2>&1
}

function git-latest-release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" |
    grep '"tag_name":' |
    sed -E 's/.*"([^"]+)".*/\1/'
  }

function kube-logs() {
  local search="$1"
  kubectl logs -f $(kubectl get pods | grep "^$search" | awk '{print $1}' | head -1)
}

function math-avg() {
  local nums=${*:-$(</dev/stdin)}
  local expr=$(echo $nums | tr ' ' '+')
  local count=$(echo $expr | grep -o '+' | grep -c '+')
  count=$((count + 1))
  echo "scale=2; ($expr)/$count" | bc
}

function math-sum() {
  local nums=${*:-$(</dev/stdin)}
  echo $nums | tr ' ' '+' | bc
}

function git-submodule-rm() {
  local module=${1:?Please specify submodule}
  module=$(echo $module | sed 's#/*$##')

  ls -ld "$module" >/dev/null || return
  ls -ld ".git/modules/$module" >/dev/null || return

  git submodule deinit -f -- "$module"
  rm -rf ".git/modules/$module"
  git rm -f "$module"
}

function git-branch-rm() {
  local branch=${1:?Please specify branch name}
  git push origin --delete "$branch"
  git branch -D "$branch"
}

function git-branch-rename() {
  local newName=${1:?Please specify new branch name}
  git branch -m "$newName"
  git push origin ":$(git branch | grep \* | cut -d ' ' -f2)" "$newName"
  git push origin -u "$newName"
}

function temperatures() {
  paste \
    <(cat /sys/class/thermal/thermal_zone*/type) \
    <(cat /sys/class/thermal/thermal_zone*/temp) \
    | column -s $'\t' -t \
    | sed 's/\(.\)..$/.\1°C/'
}

function transfer.sh() {
  curl --progress-bar --upload-file $1 https://transfer.sh/$(basename $1) | xclip
  xclip -o
  echo
}

function ls-last() {
  \ls -1trh | tail -1 | xclip -selection clipboard
  xclip -selection clipboard -o
  export last=$(xclip -selection clipboard -o)
}

function imgurbash-last() {
  # list of supported files copied from imgur website
  imgurbash "$(\ls -1trh | egrep -i '(\.jpg$|\.jpeg$|\.png$|\.gif$|\.apng$|\.tiff$|\.tif$|\.bmp$|\.pdf$|\.xcf$|\.webp$|\.mp4$|\.mov)' | tail -1)"
}

function imgurbash-last-picture() {
  cd ~/Pictures
  imgurbash-last
  cd - >/dev/null
}

function git-rm-local-commits() {
  git reset HEAD^ --hard && git clean -df && git pull
}

function precmd_tmux_rename() {
  local gitConf="$(git-go-up; pwd)/.git/config"
  local realDir=$(realpath "$(pwd)")
  if [ -r "$gitConf" ]; then
    projectName=$(grep 'url' "$gitConf" | head -1 | cut -d\= -f2 | cut -d\: -f2 | cut -d\. -f1)
    tmux rename-window " $projectName"
  elif [ "${realDir}" == "$(realpath ~/.m2/)" ]; then
    tmux rename-window "☳ ~/.m2/"
  fi
}

function precmd_history() {
  history -a
}

function preexec_tmux_rename() {
  if [ -n $TMUX ]; then
    local cmd=$(echo "$@" | sed -e 's/^\ *//' | sed -e 's/\ *$//')
    if [[ $cmd =~ ^ssh.* ]]; then
      local pid=$!
      # ssh user@host
      if [ $(echo "$cmd" | grep -c '@') -eq 1 ]; then
	local oldIFS=$IFS;
	IFS=' ';
	for token in $(echo "$cmd"); do
	  if [[ $token =~ .*@.* ]]; then
	    oldName=$(tmux display-message -p '#W')
	    echo "$oldName" > ~/.ssh/.sessions/$pid
	    ((tmux setw automatic-rename off && sleep 1.1; [ -r ~/.ssh/.sessions/$pid ] && tmux rename-window $token;) &)
	    break;
	  fi;
	done;
	IFS=$oldIFS
      else
	# ssh alias
	if [ $(echo "$cmd" | grep -o ' ' | wc -l) -eq 1 ]; then
	  local host=$(echo "$cmd" | cut -d\  -f2)
	  local user=$(grep -A5 "Host $host" ~/.ssh/config | grep 'User ' | head -1 | sed -n 's/.*User\ \(.*\)/\1/p')
	  if [ -z "$user" ]; then
	    oldName=$(tmux display-message -p '#W')
	    echo "$oldName" > ~/.ssh/.sessions/$pid
	    ((tmux setw automatic-rename off && sleep 1.1; [ -r ~/.ssh/.sessions/$pid ] && tmux rename-window "ssh $host";) &)
	  else
	    oldName=$(tmux display-message -p '#W')
	    echo "$oldName" > ~/.ssh/.sessions/$pid
	    ((tmux setw automatic-rename off && sleep 1.1; [ -r ~/.ssh/.sessions/$pid ] && tmux rename-window "${user}@${host}";) &)
	  fi
	fi
      fi
    fi
  fi
}

function aws-login() {
  $(aws ecr get-login --no-include-email --region eu-central-1)
}

function cms-deploy() {
  local namespace=${1:?Please specify deployment environment}
  local service=${2:?Please specify service name}
  local version=${3:?Please specify version}
  helm upgrade --install \
    --wait --timeout 90 \
    --version ${version} --namespace ${namespace} \
    --set image.repository=dock.tam-cms.com/${service},image.tag=${version} ${service}-${namespace} \
    kube/charts/${service}
}

function docker-container-cleanup() {
  docker container rm $(docker container ls -a | grep Exited | awk '{print $1}')
}

function docker-image-cleanup() {
  while read imageId; do
    docker-image-rm $imageId
  done< <(docker image ls --format "{{.Repository}}:{{.Tag}}:{{.ID}}" | grep '<none>:' | cut -d\: -f3)
}

function docker-image-rm() {
  local imageId=${1:?Please specify docker image id}
  local image=$(docker image ls -a --format='{{.Repository}}:{{.Tag}} {{.ID}}' | grep $imageId | cut -d\  -f1)
  if [ $(docker image ls -a | grep ${imageId} | wc -l) -gt 1 ]; then
    while read line; do
      local repo=$(echo $line | cut -d\  -f1)
      local tag=$(echo $line | cut -d\  -f2)
      docker image rm "${repo}:${tag}" 2>/dev/null
    done < <(docker image ls -a | grep ${imageId} | tr -s ' ' ' ')
  fi
  if [ $(docker container ls -a | grep -E "($image|$imageId)" | wc -l) -gt 0 ]; then
    echo ">> Deleting image containers..."
    docker container ls -a | grep -E "($image|$imageId)" | cut -d\  -f 1 | xargs docker container rm --force
  fi

  if [ $(docker image ls -a | grep -c $imageId) -gt 0 ]; then
    echo ">> Deleting image..."
    docker image rm $imageId
  fi
}

function cms-get-auth-keystore-password() {
  local namespace=${1:?Please specify deployment environment}
  kubectl -n ${namespace} get secret auth-secrets-${namespace} -o yaml | grep AUTH_KEYSTORE_PASSWORD | sed -E 's/.*: (.*)/\1/' | base64 --decode
}

function bash-history-restore() {
  largestBackup=$(ls -1S ~/.bash_history.d/currents/* | head -1)
  if [[ -r "$largestBackup" ]]; then
    cat "$largestBackup" > ~/.bash_history
    history -r
  else
    echo ">> Implement me: restore from ~/.bash_history.d/backups/"
  fi
}

function git-list-tickets() {
  local from=${1:?Please specify starting git reference}
  local to=${2:?Please specify destination git reference}
  # awk '!x[$0]++' --> removes duplicates without changing order
  git log --pretty=format:'%s' --merges --date-order "${from}..${to}" | grep -Eio 'cd2-[0-9]+'| awk '!x[$0]++'
}

function minify-js() {
  local f=${1:?Please provide file to minify inline}
  cat $f | jq . -c | tee $f
}

function jot() {
  local filename="$HOME/notes/${1}.org"
  shift
  if [ -e "$filename" ]; then
    echo -e "\n* $@" >> "$filename"
  else
    echo -e "\n* $@" >> "$HOME/notes/personal.org"
  fi
}

function cdpath() {
  local path=$(xclip -o)
  if [ -d "$path" ]; then
    cd "$path"
  else
    cd "$(dirname "$path")"
  fi
}

function garmin-scale-fit() {
  local kg=$1
  local fat_p=$2
  local water_p=$3
  local muscle_p=$4
  local bone_p=$5
  local day=$6

  if [ $# -lt 5 ]; then
    echo 'garmin-scale-fit <kg> <fat> <water> <muscle> <bone> [<day : yyyy-MM-dd>]'
    return 1
  fi

  local muscle=$(echo "scale=1; $kg * $muscle_p / 100" | bc)
  local water=$(echo "scale=1; $kg * $water_p / 100 - $muscle" | bc)
  local dry_bone=$(echo "scale=1; $kg * $bone_p / 100 - $water" | bc)
  
  weight2fit -w $kg -bf $fat_p -bw $water_p -mm $muscle -bm $dry_bone --timestamp ${day:-$(date +%Y-%m-%d)}
}

gh-browse() {
  local org=${1:-dnd-it}
  gh repo list $org -L 100 | column -t -s$'\t' | fzf | awk '{print $1}' | xargs -I {} gh repo view --web {}
}
