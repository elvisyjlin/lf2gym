#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

# Game setting
AGENT = 'Davis'
OPPOENENT = 'Dennis'
ACTIONS = [0, 0, 4, 4, 4, 2, 2, 2, 3, 3, 3, 1, 1, 1, 0, 0, 0, 9, 9, 9, 9, 0, 0, 0, 4, 0, 4, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0]

# Helper function
from time import time
def tick(msg):
    global s
    t = time()
    print('%s: %f seconds.' % (msg, t - s))
    s = t

# Add import path and import the lf2gym
import os, sys
sys.path.append(os.path.abspath('..'))

# Import lf2gym
import lf2gym
# Make an env
env = lf2gym.make(startServer=True, wrap='skip4', driverType=lf2gym.WebDriver.PhantomJS, 
    characters=[lf2gym.Character[AGENT], lf2gym.Character[OPPOENENT]], 
    difficulty=lf2gym.Difficulty.Dumbass, debug=True)

# Set the reset options
options = env.get_reset_options();
print('Original reset options: %s' % options)
options['hp_full'] = 100
options['mp_start'] = 250
print('Custom reset options: %s' % options)

# Reset the env
env.reset(options)

# Start to record the screen
env.start_recording()

# Skip 200 steps (i.e. 800 frames in skip-4 wrapping)
env.idle(200)

# Loop starts
s = time()
for act in ACTIONS:
    # Take an action
    env.step(act)
    # Render the screen
    env.render()
    # Print out the current and the previous actions as well as the time duration
    tick(env.action_info())

# Stop recording and save to a file
env.stop_recording()
env.save_recording('test.avi')