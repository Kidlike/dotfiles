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

### Tilda
* tabs and scroll not displayed -> all space is used by `tmux`
* removed most hotkeys ([mostly](https://github.com/lanoxx/tilda/issues/288))
* _note: `tilda` fully supports VTE (version 5003), whereas `guake` doesn't._

### Tmux
* tmux configs: [oh-my-tmux](https://github.com/Kidlike/oh-my-tmux) (based on [.tmux](https://github.com/gpakosz/.tmux)) with some modifications:
  * supports themes
  * faster, more maintainable
* kidlike theme is more minimal, looks good with `zenburn`.

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
