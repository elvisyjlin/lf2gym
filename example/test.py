#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import lf2gym
from lf2gym import WebDriver, Character
from time import sleep, time
from selenium.webdriver.common.action_chains import ActionChains

s = time()
def tick(msg):
    global s
    t = time()
    print('%s: %f seconds.' % (msg, t - s))
    s = t

# env = lf2gym.make(startServer=True, wrap='skip4', driverType='Chrome', captureWindowSize=(900, 1200), characters=['Woody', 'Bandit', 'Bandit', 'Bandit', 'Bandit', 'Bandit', 'Bandit', 'Bandit'])
# env = lf2gym.make(startServer=True, wrap='skip4', driverType='Chrome', captureWindowSize=(900, 1200), characters=['Woody', 'Firen'])

# env = lf2gym.make(startServer=True, wrap='skip4', driverType='PhantomJS', characters=['Firen', 'Freeze'], versusPlayer=False)
env = lf2gym.make(startServer=True, wrap='skip4', driverType=WebDriver.Chrome, characters=[Character.Firen, Character.Freeze], 
                  versusPlayer=False, duel=False, debug=True)
# driver = env.driver

opt = env.get_reset_options();
print(opt)
opt['hp_full'] = 100
opt['mp_start'] = 50
print(opt)
env.reset(opt)
sleep(100)
env.idle(200)
# env.start_screenshotting()
# print(env.env.env.get_saved_log())
# env.close()

# actions = [10, 0, 0, 0, 0, 14, 0, 0, 12, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# actions = [0, 0, 4, 2, 3, 1, 0, 0, 10, 0, 0, 14, 0, 0, 0, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
actions = [0, 0, 4, 2, 3, 1, 0, 0, 5, 0, 0, 5, 0, 0, 0, 6, 0, 0, 0, 0, 7, 0, 0, 0, 11, 0, 0, 0, 0, 0, 0, 0]
print(env.env.action_space.action_map)
print(env.env.action_space_2.action_map)
print(env.action_space.action_map)

for act in actions:
    env.step(act)
    # env.step(act, act)
    # env.render()
    print(env.action_info())
    sleep(1)