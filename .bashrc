#!/bin/bash
###
# I copied a few things from somewhere on the web (mainly from the arch forums)
###

if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# sudo completion
complete -cf sudo

# set PATH so it includes user's private bin if it exists
if [ -d ~/.bin ] ; then
PATH=~/.bin:"${PATH}"
fi

if [ -d ~/.local/bin ]; then
PATH=~/.local/bin:"${PATH}"
fi

# Global environment definitions
# ------------------------------
export PYMACS_PYTHON=python2
export HISTCONTROL=ignoredups # don't put duplicate lines in the history
export HISTCONTROL=ignoreboth # ignore same sucessive entries.
export HISTCONTROL=erasedups  # ignore duplicate entries in history
export HISTSIZE=10000         # Increases size of history
export HISTIGNORE="&:ls:ll:la:l.:pwd:exit:clear:clr:[bf]g"
shopt -s histappend   # Append history instead of overwriting
shopt -s cdspell      # Correct minor spelling errors in cd command
shopt -s dotglob      # includes dotfiles in pathname expansion
shopt -s checkwinsize # If window size changes, redraw contents
shopt -s cmdhist      # Multiline commands are a single command in history.
shopt -s extglob      # Allows basic regexps in bash.
shopt -s checkwinsize # update the values of lines and columns.
set ignoreeof on      # Typing EOF (CTRL+D) will not exit interactive sessions

# export vim as our editor
export EDITOR='vim'


# Aliases
# ---------------------------------------------------------
# get an ordered list of subdirectory sizes
alias dux='du -skh ./* | sort -h | grep -v total && du -cskh ./* | grep --color=never total'

alias install='sudo pacman -S'
alias remove='sudo pacman -Rns'
alias search='pacman -Ss'
alias update='packer -Syu'
alias searchlocal='pacman -Qs'
alias aurupdate='packer -Syu --auronly --noedit --noconfirm'
alias aurinstall='packer -S'
alias aursearch='packer -Ss'
alias aurdevel='packer -Syu --devel'

alias ..='cd ..'
alias ...='cd ../..'
alias ls='ls --color=auto'
alias l='ls -vphl --color=auto --group-directories-first --time-style="+%d-%m-%Y %H:%M"'
alias ll='ls -vphlA --color=auto --group-directories-first --time-style="+%d-%m-%Y %H:%M"'

alias grep='grep --color=auto'
alias ping='ping -c 5'
alias df='df -h'
alias clr='clear;echo "Currently logged in on $(tty), as $(whoami) in directory $(pwd)."'
alias tarc='tar -pczf'
alias tare='extract'

alias nano='vim' # In school we have to use vi ^^
alias ec='emacsclient -c -n -a nano'
alias et='emacsclient -t -a nano'

# private aliases.. e.q. ssh aliases
if [ -f ~/.bash_alias_private ]; then
    . ~/.bash_alias_private
fi



# These functions make my life easier :)
extract () {
    if [ -f $1 ] ; then
case $1 in
            *.tar.bz2) tar xvjf $1;;
            *.tar.gz) tar xvzf $1;;
            *.bz2) bunzip2 $1;;
            *.rar) unrar x $1;;
            *.gz) gunzip $1;;
            *.tar) tar xvf $1;;
            *.tbz2) tar xvjf $1;;
            *.tgz) tar xvzf $1;;
            *.zip) unzip $1;;
            *.Z) uncompress $1;;
            *.7z) 7za x $1;;
            *) echo "'$1' cannot be extracted via >extract<" ;;
        esac
else
echo "'$1' is not a valid file"
    fi
}

exip () {
    echo -n "Current External IP: "
    curl -s -m 5 http://myip.dk | grep "ha4" | sed -e 's/<b>IP Address:<\/b> <span class="ha4">//g' -e 's/<\/span><br \/><br \/>//g'
}


function psgrep () {
  ps aux | grep "$1" | grep -v "grep"
}

function mkcd () {
  mkdir -p "$1"
  cd "$1"
}

function parse_git_branch {
    git rev-parse --git-dir > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        git_status="$(git status 2> /dev/null)"
        branch_pattern="^# On branch ([^${IFS}]*)"
        detached_branch_pattern="# Not currently on any branch"
        remote_pattern="# Your branch is (.*) of"
        diverge_pattern="# Your branch and (.*) have diverged"
        untracked_pattern="# Untracked files:"
        new_pattern="new file:"
        not_staged_pattern="Changes not staged for commit"

        #files not staged for commit
        if [[ ${git_status}} =~ ${not_staged_pattern} ]]; then
            state="✔"
        fi
        # add an else if or two here if you want to get more specific
        # show if we're ahead or behind HEAD
        if [[ ${git_status} =~ ${remote_pattern} ]]; then
            if [[ ${BASH_REMATCH[1]} == "ahead" ]]; then
                remote="↑"
            else
                remote="↓"
            fi
        fi
        #new files
        if [[ ${git_status} =~ ${new_pattern} ]]; then
            remote="+"
        fi
        #untracked files
        if [[ ${git_status} =~ ${untracked_pattern} ]]; then
            remote="✖"
        fi
        #diverged branch
        if [[ ${git_status} =~ ${diverge_pattern} ]]; then
            remote="↕"
        fi
        #branch name
        if [[ ${git_status} =~ ${branch_pattern} ]]; then
            branch=${BASH_REMATCH[1]}
        #detached branch
        elif [[ ${git_status} =~ ${detached_branch_pattern} ]]; then
            branch="NO BRANCH"
        fi

        echo "[${branch}${state}${remote}]"
    fi
    return
}

# My Bash-Prompt

COLOR_RESET='\e[0m'     # Color Reset

# Regular Colors
BLACK='\e[0;30m'        # Black
RED='\e[0;31m'          # Red
GREEN='\e[0;32m'        # Green
YELLOW='\e[0;33m'       # Yellow
BLUE='\e[0;34m'         # Blue
PURPLE='\e[0;35m'       # Purple
CYAN='\e[0;36m'         # Cyan
WHITE='\e[0;37m'        # White

# Bold
BBLACK='\e[1;30m'       # Black
BRED='\e[1;31m'         # Red
BGREEN='\e[1;32m'       # Green
BYELLOw='\e[1;33m'      # Yellow
BBLUE='\e[1;34m'        # Blue
BPURPLE='\e[1;35m'      # Purple
BCYAN='\e[1;36m'        # Cyan
BWHITE='\e[1;37m'       # White

# My old command prompt
#PS1="\[$RED\]\u\[$GREEN\]@\[$YELLOW\]\h \[$BBLUE\]\w \[$RED\]$ \[$COLOR_RESET\]"

PS1="\[$WHITE\]┌─[\[$BLUE\]\u\[$WHITE\]][\[$GREEN\]\h\[$WHITE\]][\[$PURPLE\]\w\[$WHITE\]]\[$CYAN\]\$(parse_git_branch)\n\[$WHITE\]└──╼ \[$COLOR_RESET"
PS2="╾──╼ "
