#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

# Parse arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--player", default="Bandit", help="your character")
parser.add_argument("--opponent", default="Bandit", help="your enemy")
parser.add_argument("--interval", default=0.2, help="your enemy")
args = parser.parse_args()

# Add import path and import the lf2gym
import os, sys
sys.path.append(os.path.abspath('..'))

# Import lf2gym
import lf2gym
from time import sleep
# Make an env
env = lf2gym.make(startServer=True, driverType=lf2gym.WebDriver.Chrome, 
    characters=[lf2gym.Character[args.opponent], lf2gym.Character[args.player]], versusPlayer=True)
# Reset the env
env.reset()

# Game starts
done = False
while not done:
    # Sample a random action
    action = env.action_space.sample()
    # Take the chosen action
    _, reward, done, _ = env.step(action)
    print('Enemy took action %d.' % action)
    sleep(args.interval)
# Game ends
print('Gameover!')