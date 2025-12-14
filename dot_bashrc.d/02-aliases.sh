#!/bin/bash

# User specific aliases and functions
alias ..='cd ..'
alias java-switch='sdk use java $(sdk list java | grep -E "(local only|installed)" | fzf | cut -d\| -f 6 | tr -d " ")'
alias rs='ssh -t zh4747@zh4747.rsync.net'
alias tree='tree -lC'
alias l='ls'
alias la='ls -a'
alias ll='ls -l'
alias lla='ls -la'
alias open='xdg-open'
alias calcu='gcalctool'
alias mongoose='python -m http.server 7890'
alias mtail='multitail --config ~/.multitail.conf -n 102400 -m 0 -mb 100MB'
alias xclip='xclip -selection clipboard'
alias cpath='pwd | tr -d "\n" | xclip'
alias cppath='cp -pr "$(xclip -o)" .'
alias cpfrompath='cp -pr "$(xclip -o)"/* .'
alias compass-init="compass init --syntax=sass --css-dir=css --javascripts-dir=js --sass-dir=sass --images-dir=images"
alias surfraw='surfraw -browser=/usr/bin/google-chrome'
alias sr='sr -browser=/usr/bin/google-chrome'
alias pastebin="curl -sF 'clbin=<-' https://clbin.com"
alias chrome-fix-after-update='killall -9 chrome && rm -rf ~/.config/google-chrome/Default/Web\ Data'
alias pom2json='xml2json -t xml2json --pretty --strip_newlines --strip_namespace --strip_text -o pom.json'
alias jq='jq --indent 4'
alias intern-10-commands="echo \$PATH | tr ':' '\n' | xargs -I {} sh -c \"echo ==============={}; ls -1 {} | head -10\""
alias rdesktop='rdesktop -p - -g 1600x900'
alias k='kubectl'
alias kube='kubectl'
alias please='sudo'
alias ssh-github-fingerprint='ssh-keygen -l -E md5 -f'
alias pipe-audio-tardis='PULSE_SERVER=tcp:192.168.1.101'
alias count-group-by-column='echo "Counting occurences of each text in the 4th column: \"... | cut -d, -f4 | sort | uniq -c | sort -nr\""'

# color_prompt is set from ~/.bashrc
alias ls='ls -hF --color=auto --group-directories-first'
alias grep='grep --color=auto --text'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias less='less -R'

alias robot-pre="TZ=UTC MAVEN_OPTS=\"-Xms256M -Xmx1536M -XX:PermSize=256M -XX:MaxPermSize=1536m -Dfile.encoding=utf-8 -Denvironment=hudson\" mvn-dirty pre-integration-test"
alias robot-cargo="TZ=UTC MAVEN_OPTS=\"-Xms256M -Xmx1536M -XX:PermSize=256M -XX:MaxPermSize=1536m -Dfile.encoding=utf-8 -Denvironment=hudson\" mvn-dirty org.codehaus.cargo:cargo-maven2-plugin:start"
alias robot-cargo-debug="TZ=UTC MAVEN_OPTS=\"-Xms256M -Xmx1536M -XX:PermSize=256M -XX:MaxPermSize=1536m -Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y,suspend=n -Dfile.encoding=utf-8 -Denvironment=hudson\" mvn-dirty org.codehaus.cargo:cargo-maven2-plugin:start"
alias robot-clear-before-run='tmux send-keys -t! -R ; tmux clear-history -t!; tmux send-keys -R ; tmux clear-history; rm -rf $(pwd)/target/robotframework* >/dev/null; rm -rf logs >/dev/null'
alias robot-results='xdg-open $(pwd)/target/robotframework*/log.html'
alias robot-clean-mongo='mvn-dirty groovy:execute -Dsource=src/test/resources/nosql/pre-populate-docrepo-mongo.groovy -Dmongodb.prepopulate.skip=false -o'
alias robot-run="robot-clear-before-run; TZ=UTC mvn-dirty com.googlecode.robotframework-maven-plugin:robotframework-maven-plugin:run -Dexclude.tags='Exclude'"
alias robot-run-debug="robot-clear-before-run; TZ=UTC MAVEN_OPTS='-Xdebug -Xrunjdwp:transport=dt_socket,address=8001,server=y,suspend=y' mvn-dirty com.googlecode.robotframework-maven-plugin:robotframework-maven-plugin:run -Dexclude.tags='Exclude'"
alias robot2-pre="TZ=UTC MAVEN_OPTS=\"-Xms256M -Xmx1536M -XX:PermSize=256M -XX:MaxPermSize=1536m -Dfile.encoding=utf-8 -Denvironment=hudson\" mvn-dirty -f pom-new-ats.xml pre-integration-test"
alias robot2-cargo="TZ=UTC MAVEN_OPTS=\"-Xms256M -Xmx1536M -XX:PermSize=256M -XX:MaxPermSize=1536m -Dfile.encoding=utf-8 -Denvironment=hudson\" mvn-dirty -f pom-new-ats.xml org.codehaus.cargo:cargo-maven2-plugin:start"
alias robot2-cargo-debug="TZ=UTC MAVEN_OPTS=\"-Xms256M -Xmx1536M -XX:PermSize=256M -XX:MaxPermSize=1536m -Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y,suspend=n -Dfile.encoding=utf-8 -Denvironment=hudson\" mvn-dirty -f pom-new-ats.xml org.codehaus.cargo:cargo-maven2-plugin:start"
alias robot2-run="robot-clear-before-run; TZ=UTC mvn-dirty -f pom-new-ats.xml org.robotframework:robotframework-maven-plugin:run -Dexclude.tags='Exclude'"
alias robot2-run-debug="robot-clear-before-run; TZ=UTC MAVEN_OPTS='-Xdebug -Xrunjdwp:transport=dt_socket,address=8001,server=y,suspend=y' mvn-dirty -f pom-new-ats.xml org.robotframework:robotframework-maven-plugin:run -Dexclude.tags='Exclude'"

alias mvn-dirty="mvn -Dcobertura.skip=true -Dfindbugs.skip=true -Dcheckstyle.skip=true -Djasmine.skip=true -DfailIfNoTests=false"
alias mvn-dirty-test="mvn -Dcobertura.skip=true -Dfindbugs.skip=true -Dcheckstyle.skip=true -Djasmine.skip=true -DfailIfNoTests=false clean test"
alias mvn-dirty-test-debug="mvn -Dcobertura.skip=true -Dfindbugs.skip=true -Dcheckstyle.skip=true -Djasmine.skip=true -DfailIfNoTests=false -Dmaven.surefire.debug clean test"
alias mvn-dirty-install="mvn-dirty -DskipTests -Dmaven.test.skip=true -Dcargo.maven.skip=true clean install"
alias mvn-dirty-package="mvn-dirty -DskipTests -Dmaven.test.skip=true -Dcargo.maven.skip=true clean package"
alias mvn-build-n-deploy='mvn-dirty-install -o && mvn-tomcat-deploy'
alias mvn-pitest='mvn-dirty clean test site -Dpitest'
alias mvntail='mtail -cS maven'

alias vagrant-remove-all-boxes="vagrant box list | cut -f 1 -d ' ' | xargs -L 1 vagrant box remove -f"
alias memory-release-inactive='sync && echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null'
alias update-grub='sudo grub2-mkconfig -o /boot/grub2/grub.cfg; sudo grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg'
alias kernel-lock='sudo dnf versionlock add $(rpm -qa | grep -E "^kernel.*$(uname -r)")'

alias tam='cd ~/tx/repos/dnd-it/'
alias tam-cms='cd ~/tx/repos/dnd-it/cms'
alias tam-cms-wiki='cd ~/tx/repos/dnd-it/cms.wiki'
alias tam-cms-front='cd ~/tx/repos/dnd-it/cms-frontend'
alias tam-jenkins-lib='cd ~/tx/repos/dnd-it/jenkins-shared-libs-2'
alias tam-devops='cd ~/tx/repos/dnd-it/devops'

alias stef='cd ~/stef/code/'
alias stef-dots='cd ~/stef/code/dotfiles'
alias stef-sys='cd ~/stef/code/system-config'
alias stef-bash-it='cd ~/stef/code/bash-it'
alias memory-usage='smem -t -k -P'
