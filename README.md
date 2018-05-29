# dotfiles
my dotfiles 🤙

## Install
* Installation uses [dotbot](https://github.com/anishathalye/dotbot)
* Will create softlinks based on `install.conf.yaml`
* The install script is idempotent (will produce the same result on subsequent executions)
```
git clone --recursive git@github.com:Kidlike/dotfiles.git
cd dotfiles
./install.bsh
```

## Terminal
* Setup composition: `tilda -> tmux -> xterm-256color -> bash`
* Font: `Source Code Pro 11`
* Semi-transparent

### Tilda (drop-down terminal)
* tabs and scroll not displayed -> all space is used by `tmux`
* removed most hotkeys ([mostly](https://github.com/lanoxx/tilda/issues/288))
* _note: `tilda` fully supports VTE (version 5003), whereas `guake` doesn't._

### Tmux
* tmux configs: [oh-my-tmux](https://github.com/Kidlike/oh-my-tmux) (based on [.tmux](https://github.com/gpakosz/.tmux)) with some modifications:
  * supports themes
  * faster, more maintainable
* kidlike theme is more minimal, looks good with `zenburn`.
* custom status line
  * left
    * tmux windows
* custom status line
  * right (color coded)
    * battery percentage
    * time / date
    * username
    * hostname
* working directory is maintained when openning panes/windows.

### Bash
* prompt cursor: `_`
* `~/.bashrc` stays untouched. the machine's local copy will be appended to the configuration.
* The configs are loaded by `~/.bash_profile` which means will only work for login shells.
* Command history is curated by `~/.bash_logout`
  * Command history from other shells can be appended in current shell `exec bash -li`
* Uses [fzf](https://github.com/junegunn/fzf)
* Uses [bash-preexec](https://github.com/rcaloras/bash-preexec)
* Uses [bash-it](https://github.com/Kidlike/bash-it) with a custom theme (powerline-naked-multiline)
  * powerline-like theme
  * segments:
    * kubernetes namespace (conditional)
    * username
    * git info (conditional)
    * working directory
    * last status code (conditional)

### Vim
* insert mode cursor: `|`
* vim configs based on [audibleblink/dotbot](https://github.com/audibleblink/dotbot)
* added custom powerline-like statusbar
* removed any unused plugins

## Hotkeys
* `F1` opens terminal (tilda)
* `ctrl-c/v` as per normal
* `ctrl-r` fzf

### Tmux
#### Basics
* `alt-a` prefix
* `alt-0`-`alt-9` switch to tab 0-9. first tab is 1, last tab is 0
* `alt-t` `alt-a t` new tab
* `alt-w` `alt-a tab` select window
* `alt-q` `alt-a q` help with hotkeys
* `alt-l` clear output buffer (like ctrl+l but better)

#### Panes
* `alt--` `alt-a -` create pane horizontally
* `alt-\` `alt-a \` create pane vertically
* `alt-|` `alt-a |` create pane vertically
* `alt-left` `alt-a left` select left pane
* `alt-right` `alt-a right` select right pane
* `alt-down` `alt-a down` select down pane
* `alt-up` `alt-a up` select up pane
* `alt-a h` move vertical split line to the left
* `alt-a l` move vertical split line to the right
* `alt-a j` move horizontal split line down
* `alt-a k` move horizontal split line up

#### Advanced (or not?)
* `alt-z` `alt-a z` Zoom-in (maximizes pane)
* `alt-a m` toggle mouse mode on/off
* `alt->` send pane to window number
* `alt-<` retrieve pane from window number
* `alt-m` open manpage for given command (in new pane)
* `alt-c` run given command (in new pane)
* `alt-d` detaching is disabled
* `alt-e` `alt-a s` select session
* `alt-n` `alt-a n` go to next window
* `alt-p` `alt-a p` go to previous window
* `alt-a @` kill window (with prompt)
* `alt-a c` kill pane (without prompt)
* `alt-[` `alt-a {` swap panes clockwise
* `alt-]` `alt-a }` swap panes counter-clockwise

## Screenshots
<img src="https://i.imgur.com/tBnjxfC.jpg" width="500px"/>
<img src="https://i.imgur.com/VdYa2M3.png" width="500px"/>
<img src="https://i.imgur.com/rxc5Nn2.png" width="500px"/>
<img src="https://i.imgur.com/72ptmc4.png" width="500px"/>
<img src="https://i.imgur.com/Z6qcKsp.png" width="500px"/>
