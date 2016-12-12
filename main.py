# -*- coding: utf-8 -*-
#!/usr/bin/env python


from definability import *

def main():

    from IPython.terminal.embed import InteractiveShellEmbed

    ipshell = InteractiveShellEmbed(banner1 = 'Definability\n', exit_msg = 'Leaving Definability')

    ipshell('Hit Ctrl-D to exit interpreter.\n')

if __name__ == "__main__":
    main()
