# [.] dotfiles

These are my personal dotfiles for Arch Linux, Debian and OS X.
I am using the Vim configuration from
[amix/vimrc](https://github.com/amix/vimrc) and the emacs configuration is
called [bbatsov/prelude](https://github.com/bbatsov/prelude).

## Installation

First of all, clone the repo to somewhere.

    git clone https://github.com/sh4nks/dotfiles ~/Development/dotfiles

After this, you need to initialize the `git submodules`. For this, you have to
go to the location where you cloned the repository.

    cd ~/Development/dotfiles

and run following command

    git submodule init && git submodule update

Now you got all the packages which are needed and can finally proceed with
symlinking the dotfiles. To make it easier, I created a Makefile. To see
the list with available commands simply type in the `dotfiles` directory:

    make


**Attention:** The next step will overwrite your current dotfiles!

To install the Linux specific dotfiles type:

    make install-linux

and for OSX:

    make install-osx



To install these configuration files you just need to type `make install`.


# LICENSE

Some files in this directory might be licensed in different forms and I do not
give a guarantee for the cleaness of the combined work.  My personal
modifications to files or creations in this file can be seen to be written
under the MIT license:


    The MIT License (MIT)

    Copyright (c) 2015 sh4nks

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
