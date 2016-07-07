# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""An example of how to embed an IPython shell into a running program.

Please see the documentation in the IPython.Shell module for more details.

The accompanying file embed_class_short.py has quick code fragments for
embedding which you can cut and paste in your code once you understand how
things work.

The code in this file is deliberately extra-verbose, meant for learning."""
from __future__ import print_function

# The basics to get you going:

# IPython injects get_ipython into builtins, so you can know if you have nested
# copies running.

# Try running this code both at the command line and from inside IPython (with
# %run example-embed.py)
from traitlets.config import Config
from definability import *

def main():
    nested = 0
    cfg = Config()
    prompt_config = cfg.PromptManager
    prompt_config.in_template = 'In <\\#>: '
    prompt_config.in2_template = '   .\\D.: '
    prompt_config.out_template = 'Out<\\#>: '


    # First import the embeddable shell class
    from IPython.terminal.embed import InteractiveShellEmbed

    # Now create an instance of the embeddable shell. The first argument is a
    # string with options exactly as you would type them if you were starting
    # IPython at the system command line. Any parameters you want to define for
    # configuration can thus be specified here.
    ipshell = InteractiveShellEmbed(config=cfg,
                           banner1 = 'Definability\n',
                           exit_msg = 'Leaving Definability')


    ipshell('Hit Ctrl-D to exit interpreter.\n')

if __name__ == "__main__":
    main()
