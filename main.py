# -*- coding: utf-8 -*-
#!/usr/bin/env python


from definability import *

def main():

    # First import the embeddable shell class
    from IPython.terminal.embed import InteractiveShellEmbed

    # Now create an instance of the embeddable shell. The first argument is a
    # string with options exactly as you would type them if you were starting
    # IPython at the system command line. Any parameters you want to define for
    # configuration can thus be specified here.
    ipshell = InteractiveShellEmbed(banner1 = 'Definability\n',
                                    exit_msg = 'Leaving Definability')


    ipshell('Hit Ctrl-D to exit interpreter.\n')

if __name__ == "__main__":
    main()
