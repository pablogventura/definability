#!/usr/bin/env python
# -*- coding: utf8 -*-

def indent(text):

    text = "  " + text.strip("\n") 
    return text.replace('\n', '\n  ') + "\n"
