install: install-vim install-bash install-python \
         install-git

install-vim:
	rm -rf ~/.vim ~/.vimrc
	ln -s `pwd`/vim ~/.vim
	ln -s ~/.vim/vimrc ~/.vimrc

install-emacs:
	rm -rf ~/.emacs.d
	ln -s `pwd`/emacs.d ~/.emacs.d

install-bash:
	rm -f ~/.bashrc
	ln -s `pwd`/bash/bashrc ~/.bashrc

install-osx:
	rm -f ~/.bashrc
	rm -f ~/.bash_profile
	ln -s `pwd`/bash_osx/bashrc ~/.bashrc
	ln -s `pwd`/bash_osx/bash_profile ~/.bash_profile

install-git:
	rm -f ~/.gitconfig
	ln -s `pwd`/git/gitconfig ~/.gitconfig

