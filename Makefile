help:
	@echo "  install-linux		dotfiles for linux"
	@echo "  install-osx		dotfiles for osx"
	@echo "  =========== single commands ==========="
	@echo "  install-git		git dotfiles"
	@echo "  install-bash		bash dotfiles"
	@echo "  install-bash-osx	bash_profile for osx"
	@echo "  install-emacs		emacs dotfiles"
	@echo "  install-vim		vim dotfiles"
	@echo "  install-vim-basic	vim basic dotfiles (without plugins)"
	@echo "  install-scripts	installs some scripts"


install-linux: install-vim install-emacs install-bash install-git install-scripts

install-osx: install-vim install-emacs install-bash-osx install-git

install-vim:
	rm -rf ~/.vim ~/.vim_runtime ~/.vimrc
	ln -sfT `pwd`/vim ~/.vim_runtime
	sh `pwd`/vim/install_awesome_vimrc.sh

install-vim-basic:
	rm -rf ~/.vim ~/.vimrc
	ln -sfT `pwd`/vim ~/.vim
	sh `pwd`/vim/install_basic_vimrc.sh

install-emacs:
	rm -rf ~/.emacs.d
	ln -sfT `pwd`/emacs.d ~/.emacs.d

install-bash:
	rm -f ~/.bashrc
	ln -sfT `pwd`/bash/ ~/.bash.d
	ln -sfT ~/.bash.d/bashrc ~/.bashrc

install-bash-osx: install-bash
	rm -f ~/.bash_profile
	ln -sfT ~/.bash.d/bash_profile ~/.bash_profile

install-git:
	rm -f ~/.gitconfig
	ln -sfT `pwd`/git ~/.git.d
	ln -sfT ~/.git.d/gitconfig ~/.gitconfig

install-scripts:
	ln -sfT `pwd`/scripts/clean_yay_cache.py ~/.bin/clean_yay_cache.py
