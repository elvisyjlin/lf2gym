#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

import numpy as np
from . import config
from collections import deque

class LF2Wrapper():
    def __init__(self, env, mem_len=4):
        self.env = env
        self.action_space = env.action_space
        self.observation_space = config.ObservationSpace((160, 380, mem_len))
        self.mem_len = mem_len
        self.frames = deque([], maxlen=mem_len)
        
        self.characters = env.characters
        self.background = env.background

    def step(self, *action):
        observation, reward, done, info = self.env.step(*action)
        self.frames.append(observation)
        return self.observe(), reward, done, info

    def render(self, label=None):
        self.env.render(label)

    def reset(self, options=None):
        observation = self.env.reset(options)
        for _ in range(self.mem_len):
            self.frames.append(observation)
        return self.observe()

    def observe(self):
        return np.stack(self.frames, axis=2)

    def idle(self, duration=0): self.env.idle(duration)
    def get_log(self): return self.env.get_saved_log()
    def get_detail(self): return self.env.get_detail()
    def get_reset_options(self): return self.env.get_reset_options();
    def start_recording(self): self.env.start_recording()
    def stop_recording(self): self.env.stop_recording()
    def save_recording(self, name): self.env.save_recording(name)
    def debug(self, name): self.env.debug(name)
    def close(self): self.env.close()
    def render_out(self): self.env.render_out()
    def reduce_action_space(self, len): self.action_space.reduce(len)
    def start_screenshotting(self): self.env.start_screenshotting()

class LF2SkipNWrapper():
    def __init__(self, env, num_frame, mem_len=4, character=None, options=None, debug=False):
        self.env = env
        self.mem_len = mem_len
        self.frames = deque([], maxlen=mem_len)

        self.action_space = config.SkipNActionSpace(num_frame=num_frame, character=character, options=options)
        self.observation_space = self.env.observation_space
        
        self.characters = env.characters
        self.background = env.background

        self.debugMode = debug
        self.prev_action = None
        self.curr_action = None

    def step(self, *skip4_action):
        observation, reward, done, info = None, 0, False, True
        actions = [self.action_space.get(skip4) for skip4 in skip4_action]
        for action in zip(*actions):
            o, r, d, i = self.env.step(*action)
            observation = o
            reward += r
            done = done or d
            info = info and i
        self.frames.append(observation)
        self.prev_action = self.curr_action
        self.curr_action = skip4_action
        return self.observe(), reward, done, info

    def render(self):
        self.env.render(self.action_info() if self.debugMode else None)
        
    def reset(self, options=None):
        observation = self.env.reset(options)
        for _ in range(self.mem_len):
            self.frames.append(observation)
        return self.observe()

    def observe(self):
        return np.stack(self.frames, axis=2)

    def idle(self, duration=0): self.env.idle(duration)
    def get_log(self): return self.env.get_log()
    def get_detail(self): return self.env.get_detail()
    def get_reset_options(self): return self.env.get_reset_options();
    def start_recording(self): self.env.start_recording()
    def stop_recording(self): self.env.stop_recording()
    def save_recording(self, name): self.env.save_recording(name)
    def debug(self, name='debug'): self.env.debug(name)
    def close(self): self.env.close()
    def render_out(self): self.env.render_out()
    def reduce_action_space(self, len): self.action_space.reduce(len)
    def start_screenshotting(self): self.env.start_screenshotting()
    def action_info(self):
        if self.prev_action is None:
            return 'Current action: None | Previous action: None'
        elif self.curr_action is None:
            return 'Current action: %s | Previous action: None' % (self.curr_action)
        else:
            return 'Current action: %s | Previous action: %s' % (self.curr_action, self.prev_action)
