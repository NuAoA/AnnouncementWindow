import sys

class platform:
    win = (sys.platform == 'win32')
    osx = (sys.platform == 'darwin')
    linux = (sys.platform == 'linux2' or sys.platform == 'linux')
    unix = (osx or linux)

class mouse_buttons:
    left = '<Button-1>'
    right = '<Button-3>' if not platform.osx else '<Button-2>'
    middle = '<Button-2>' if not platform.osx else '<Button-3>'
