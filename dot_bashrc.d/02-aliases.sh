#!/bin/bash

# generic
alias ..='cd ..'
alias l='ls'
alias la='ls -a'
alias ll='eza --group-directories-first -l'
alias lla='ll -a'
alias tree='tree -lC'
alias open='xdg-open'
alias xclip='xclip -selection clipboard'
alias cpath='pwd | tr -d "\n" | xclip'
alias pastebin="curl -sF 'clbin=<-' https://clbin.com"
alias jq='jq --indent 4'
alias please='sudo'
alias mongoose='python -m http.server 7890'
alias path-commands="echo \$PATH | tr ':' '\n' | xargs -I {} sh -c \"echo ==============={}; ls -1 {} | head -10\""
alias pom2json='xml2json -t xml2json --pretty --strip_newlines --strip_namespace --strip_text -o pom.json'
alias count-group-by-column='echo "Counting occurences of each text in the 4th column: \"... | cut -d, -f4 | sort | uniq -c | sort -nr\""'
alias java-switch='sdk use java $(sdk list java | grep -E "(local only|installed)" | fzf | cut -d\| -f 6 | tr -d " ")'
alias mvn-spotbugs-gui='mvn spotbugs:gui -Dsun.java2d.uiScale=2.0'
#alias serena='uvx --from git+https://github.com/oraios/serena serena'
alias tmux-capture-pane='tmux capture-pane -epS - > ~/tmux.out'
alias gh-pr="gh pr view --web 2>/dev/null || gh pr create --web"

# colors
alias ls='ls -hF --color=auto --group-directories-first'
alias grep='grep --color=auto --text'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias less='less -R'
alias eza='eza --color=always'

# kubernetes
alias k='kubectl'
alias kcx='kubie ctx'
alias kns='kubie ns'

# changes system state
alias update-grub='sudo grub2-mkconfig -o /boot/grub2/grub.cfg; sudo grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg'
alias kernel-lock='sudo dnf versionlock add $(rpm -qa | grep -E "^kernel.*$(uname -r)")'

# memory
alias memory-usage='smem -t -k -P'
alias memory-release-inactive='sync && echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null'

