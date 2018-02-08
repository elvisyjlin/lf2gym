#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

from .lf2exception import lf2raise

from enum import Enum
from selenium.webdriver.common.keys import Keys
from random import randint

class StrIntEnum(Enum):
    def __str__(self):
        return self.value[0]
    def __int__(self):
        return self.value[1]

class WebDriver(StrIntEnum):
    PhantomJS   = 'PhantomJS',  1
    Chrome      = 'Chrome',     2
    Firefox     = 'Firefox',    3

class Character(StrIntEnum):
    Bandit      = 'Bandit', 1
    Deep        = 'Deep',   2
    John        = 'John',   3
    Louis       = 'Louis',  4
    Firen       = 'Firen',  5
    Freeze      = 'Freeze', 6
    Dennis      = 'Dennis', 7
    Woody       = 'Woody',  8
    Davis       = 'Davis',  9


class Difficulty(StrIntEnum):
    Dumbass     = 'dumbass',        1
    Challengar  = 'CHALLANGAR 1.0', 2
    Crusher     = 'CRUSHER 1.0',    3

class Background(StrIntEnum):
    HK_Coliseum     = 'HK Coliseum',     1
    Lion_Forest     = 'Lion Forest',     2
    Stanley_Prison  = 'Stanley Prison',  3
    The_Great_Wall  = 'The Great Wall',  4
    Queens_Island   = 'Queen\'s Island', 5
    Forbidden_Tower = 'Forbidden Tower', 6
    CUHK            = 'CUHK',            7
    Tai_Hom_Village = 'Tai Hom Village', 8
    Template1       = 'Template1',       9

action_map = {
    0:  [],         # idle
    1:  ['w'],      # up
    2:  ['x'],      # down
    3:  ['a'],      # left
    4:  ['d'],      # right
    5:  ['s'],      # atk
    6:  ['q'],      # jump
    7:  ['z'],      # def
    8:  ['a', 'a'], # run left
    9:  ['d', 'd'], # run right
    10: ['w', 'd'], # up right
    11: ['x', 'd'], # down right
    12: ['w', 'a'], # up left
    13: ['x', 'a']  # down left
}

action_map_2 = {
    0:  [],                                     # idle
    1:  [Keys.ARROW_UP],                        # up
    2:  [Keys.ARROW_DOWN],                      # down
    3:  [Keys.ARROW_LEFT],                      # left
    4:  [Keys.ARROW_RIGHT],                     # right
    5:  ['j'],                                  # atk
    6:  ['u'],                                  # jump
    7:  ['m'],                                  # def
    8:  [Keys.ARROW_LEFT, Keys.ARROW_LEFT],     # run left
    9:  [Keys.ARROW_RIGHT, Keys.ARROW_RIGHT],   # run right
    10: [Keys.ARROW_UP, Keys.ARROW_RIGHT],      # up right
    11: [Keys.ARROW_DOWN, Keys.ARROW_RIGHT],    # down right
    12: [Keys.ARROW_UP, Keys.ARROW_LEFT],       # up left
    13: [Keys.ARROW_DOWN, Keys.ARROW_LEFT]      # down left
}

skip4_action_map = {
    0:  [0, 0, 0, 0],     # idle
    1:  [1, 1, 1, 1],     # ^
    2:  [2, 2, 2, 2],     # v
    3:  [3, 3, 3, 3],     # <
    4:  [4, 4, 4, 4],     # >

    5:  [10, 10, 10, 10], # ^>
    6:  [11, 11, 11, 11], # v>
    7:  [12, 12, 12, 12], # ^<
    8:  [13, 13, 13, 13], # v<

    9:  [8, 0, 0, 0],    # < <
    10: [9, 0, 0, 0],    # > >

    11: [5, 0, 0, 0],     # A
    12: [6, 0, 0, 0],     # J
    13: [7, 0, 0, 0],     # D

    14: [7, 3, 5, 0],     # D < A
    15: [7, 4, 5, 0],     # D > A
    16: [7, 3, 6, 0],     # D < J
    17: [7, 4, 6, 0],     # D > J
    18: [7, 1, 5, 0],     # D ^ A
    19: [7, 2, 5, 0],     # D v A
    20: [7, 1, 6, 0],     # D ^ J
    21: [7, 2, 6, 0]      # D v J
}

keyCode = {
    'w': 87, 
    'd': 68, 
    'x': 88, 
    'a': 65, 
    Keys.ARROW_UP: 38, 
    Keys.ARROW_RIGHT: 39, 
    Keys.ARROW_DOWN: 40, 
    Keys.ARROW_LEFT:37
}

action_sequence_mapping = {
    'Basic':          [0, 1, 2, 3, 4], 
    'Advanced':       [5, 6, 7, 8], 
    'Run':            [9, 10], 
    'AJD':            [11, 12, 13], 
    'Full Combos':    [14, 15, 16, 17, 18, 19, 20, 21], 
    'No Combos':      [], 
    Character.Bandit: [], 
    Character.Deep:   [14, 15, 16, 17, 19, 20], 
    Character.John:   [14, 15, 16, 17, 18, 20, 21], 
    Character.Louis:  [14, 15, 16, 17, 20], 
    Character.Firen:  [14, 15, 16, 17, 20, 21], 
    Character.Freeze: [14, 15, 16, 17, 20, 21], 
    Character.Dennis: [14, 15, 16, 17, 18, 19], 
    Character.Woody:  [14, 15, 16, 17, 18, 19, 20, 21], 
    Character.Davis:  [14, 15, 18, 19, 20]
}

def filter_action_map(action_map, filter):
    index = 0
    new_action_map = {}
    for idx, act in sorted(action_map.items()):
        if idx in filter:
            new_action_map[index] = act
            index += 1
    return new_action_map

def create_skip_4_action_space(character, options):
    filter = sum([action_sequence_mapping[option] for option in (options + [character])], [])
    if 'No Combos' in options:
        filter = [option for option in filter if option not in action_sequence_mapping['Full Combos']]
    return filter_action_map(skip4_action_map, filter)

def extend_action_map_sequence(action_map, length=0):
    for idx, seq in action_map.items():
        action_map[idx] = seq + [seq[-1]] * length
    return action_map

class ActionSpace():
    def __init__(self, player=1):
        if player != 1 and player != 2: lf2raise('ActionSpace Error.')
        if player == 1:
            self.action_map = action_map
        else:
            self.action_map = action_map_2
        self.n = len(self.action_map)
    def get(self, i):
        if i < 0 or i >= self.n: lf2raise('Action should be in (0, %d), rather than %d.' % (self.n-1, i))
        return self.action_map[i]
    def sample(self):
        return randint(0, self.n-1)
    def reduce(self, len):
        self.n = len

class SkipNActionSpace():
    def __init__(self, num_frame, character=None, options=[]):
        if num_frame < 4: lf2raise('num_frame "%d" should be at least 4.' % num_frame)
        self.action_map = extend_action_map_sequence(create_skip_4_action_space(character, options), num_frame-4)
        self.n = len(self.action_map)
    def get(self, i):
        if i < 0 or i >= self.n: lf2raise('Action should be in (0, %d), rather than %d.' % (self.n-1, i))
        return self.action_map[i]
    def sample(self):
        return randint(0, self.n-1)
    # def reduce(self, len):
    #     self.n = len

class ObservationSpace():
    def __init__(self, size):
        self.n = size
