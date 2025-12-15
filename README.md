## Quickstart

```shell
sudo dnf copr enable scottames/ghostty
sudo dnf copr enable atim/starship
sudo dnf install ghostty starship chezmoi fzf xclip bat zoxide
cargo install eza
curl --proto '=https' --tlsv1.2 -LsSf https://setup.atuin.sh | sh
chezmoi init --apply Kidlike
```
## Intended workflow
- full screen drop-down terminal (ghostty), with a shortcut
   - not registering as a window (not available for alt-tab)
   - available to all virtual desktops
   - no decorations from window manager nor ghostty
- ghostty runs tmux
   - via tmux-restore.sh, which auto-detects to start a new session or attach to an existing one
- tmux for windows, panes, and quickly clearing the scrollback
   - tmux sessions via tmux-tea, very easy - it just remembers your projects
   - 2kabhishek/tmux2 for statusbar
- bash
   - atuin for shell history sync, and ctrl+r (has some more features than fzf)
   - starship for PS1

### Other notes
- the whole thing should be very fast (no slow configs/plugins allowed)
- tmux plugins must be available through TPM

