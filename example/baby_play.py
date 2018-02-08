#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--player", default="Bandit", help="your character")
parser.add_argument("--opponent", default="Bandit", help="your enemy")
parser.add_argument("--interval", default=0.2, help="your enemy")
args = parser.parse_args()


import sys
lf2gymPath = '..'
sys.path.append(lf2gymPath)

import lf2gym
from time import sleep
env = lf2gym.make(startServer=True, driverType=lf2gym.WebDriver.Chrome, 
    characters=[lf2gym.Character[args.opponent], lf2gym.Character[args.player]], versusPlayer=True, lf2gymPath=lf2gymPath)
env.reset()

done = False
while not done:
    action = env.action_space.sample()
    _, reward, done, _ = env.step(action)
    print('Enemy took action %d.' % action)
    sleep(args.interval)
print('Gameover!')