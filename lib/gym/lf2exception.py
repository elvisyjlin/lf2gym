#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

"""lf2exception.py: An exception class for LF2-Gym."""

class LF2Exception(Exception):
    pass

def lf2raise(message):
    raise LF2Exception(message)