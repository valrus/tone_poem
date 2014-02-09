## A Crazy Idea

Code for a really long-shot, super-insane idea I had for a project involving Kivy and MIDI input.

I used shadowmint's [kivy-buildout](https://github.com/shadowmint/kivy-buildout) as a starting point. Here's my very rough list of steps to get Kivy 1.8 stable working (modulo bugs in Kivy itself) with Python 3 and [python-rtmidi](https://pypi.python.org/pypi/python-rtmidi) in a buildout in OS X:

1. mkvirtualenv -p /usr/local/bin/python3 kivy
2. pip install --ignore-installed --install-option="--prefix=/Users/valrus/.envs/kivy/" cython
3. hg clone http://bitbucket.org/pygame/pygame
4. Install [pygame](http://jalada.co.uk/2011/06/17/installing-pygame-on-os-x-with-a-homebrew-python-2-7-install.html) (I could not get pygame to find SDL without doing this sort of ugly workaround)
5. git clone https://github.com/kivy/kivy.git
6. Apply [this fix](https://github.com/kivy/kivy/pull/1838)
7. cd kivy; python setup.py install
8. git clone https://github.com/shadowmint/kivy-buildout
9. edit buildout.cfg and change "eggs =" section to just have python-rtmidi
