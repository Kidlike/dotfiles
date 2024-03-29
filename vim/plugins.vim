set nocompatible
filetype off
call plug#begin('~/.vim/plugged')

"Plug 'airblade/vim-gitgutter'
"Plug 'christoomey/vim-tmux-navigator'
Plug 'jiangmiao/auto-pairs'
"Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }
"Plug 'junegunn/fzf.vim'
Plug 'junegunn/vim-easy-align'
Plug 'justinmk/vim-sneak'
Plug 'kana/vim-textobj-user' 
Plug 'maralla/completor.vim'
Plug 'w0rp/ale'
Plug 'sheerun/vim-polyglot'
"Plug 'terryma/vim-multiple-cursors'
Plug 'tomtom/tcomment_vim'
Plug 'tpope/vim-endwise'
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-sleuth'
Plug 'tpope/vim-surround'
Plug 'junegunn/goyo.vim'
Plug 'ekalinin/Dockerfile.vim'
Plug 'chrisbra/csv.vim'

"Plug 'vimwiki/vimwiki'
"Plug 'suan/vim-instant-markdown',      { 'for': 'markdown' }

"Plug 'chrisbra/vim-zsh',               { 'for': 'zsh' }
Plug 'fatih/vim-go',                   { 'for': 'go' }
Plug 'freitass/todo.txt-vim',          { 'for': 'txt' }
Plug 'mattn/emmet-vim',                { 'for': ['html', 'javascript.jsx'] }

call plug#end()
filetype plugin indent on

" Instant Markdown
  let g:instant_markdown_autostart = 0

" Go Completor
  let g:completor_gocode_binary = 'gocode'

" Colorscheme
  syntax on
  if has('termguicolors')
    set termguicolors
    set t_ut=
  endif
  "set background=light
  colorscheme onedark
  "colorscheme github
  "colorscheme wombat
  "colorscheme zenburn

  hi CursorLine cterm=None
  let g:onedark_terminal_italics = 1

" RSpec.vim mappings
  let g:rspec_command = "VtrSendCommandToRunner! zeus rspec {spec}"

" VimWiki
  let g:vimwiki_list = [{'path': '~/private/VimWiki/index.wiki'}]

" Tmux Navigator
  " Send :update when leaving vim for tmux
  let g:tmux_navigator_save_on_switch = 1

" FZF
  " Layout
  let g:fzf_layout = { 'down': '~35%'  }

" EasyAlign
  " Start interactive EasyAlign in visual mode (e.g. vipga)
  xmap ga <Plug>(EasyAlign)
  " Start interactive EasyAlign for a motion/text object (e.g. gaip)
  nmap ga <Plug>(EasyAlign)
