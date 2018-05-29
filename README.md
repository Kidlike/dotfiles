# dotfiles
my dotfiles 🤙

## Install
* Installation uses [dotbot](https://github.com/anishathalye/dotbot)
* Will create softlinks based on `install.conf.yaml`
```
git clone --recursive git@github.com:Kidlike/dotfiles.git
cd dotfiles
./install.bsh
```

## Terminal Features
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
* working directory is maintained when openning panes/windows.

### Bash
* `~/.bashrc` stays untouched. the machine's local copy will be appended to the configuration.
* The configs are loaded by `~/.bash_profile` which means will only work for login shells.
* Command history is curated by `~/.bash_logout`
  * Command history from other shells can be appended in current shell `exec bash -li`
* Uses [bash-it](https://github.com/Kidlike/bash-it) with a custom theme (powerline-naked-multiline)
* Uses [fzf](https://github.com/junegunn/fzf)
* Uses [bash-preexec](https://github.com/rcaloras/bash-preexec)

### Vim
* vim configs based on [audibleblink/dotbot](https://github.com/audibleblink/dotbot)
* added custom powerline-like statusbar
* removed any unused plugins

## Hotkeys
* `F1` opens terminal (tilda)
* `ctrl-c/v` as per normal

### Tmux
#### Basics
* `alt-a` prefix
* `alt-0`-`alt-9` switch to tab 0-9. first tab is 1, last tab is 0
* `alt-t` `alt-a t` new tab
* `alt-w` `alt-a tab` select window
* `alt-q` `alt-a q` help with hotkeys

#### Splitting
* `alt--` `alt-a -` create pane horizontally
* `alt-\` `alt-a \` create pane vertically
* `alt-|` `alt-a |` create pane vertically
* `alt-left` `alt-a left` select left pane
* `alt-right` `alt-a right` select right pane
* `alt-down` `alt-a down` select down pane
* `alt-up` `alt-a up` select up pane


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
