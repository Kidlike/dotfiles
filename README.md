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
- tmux plugins must be available through TPM
- bash with atuin + starship

