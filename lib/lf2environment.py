#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

from . import config
from . import seleniumdriver
from .lf2exception import lf2raise
from .utils import png2rgb, rgb2gray, Recorder

import atexit
import json
import numpy as np
import platform
import signal
import sys

from PIL import Image
from glob import glob
from scipy.misc import imresize
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from time import sleep
from os import mkdir, system, remove
from os.path import abspath, exists, join

SLEEP_DURATION = 2
NOTSET = -1e4
REWARD_HP_FACTOR = [] # {'Firen': -1, 'Freeze': +1}
REWARD_MP_FACTOR = [] # {'Firen': -1, 'Freeze': 0}
OPPOSITE_KEYS = {'w': 'x', 'x': 'w', 'd': 'a', 'a': 'd', 
    Keys.ARROW_UP: Keys.ARROW_DOWN, Keys.ARROW_DOWN: Keys.ARROW_UP, 
    Keys.ARROW_LEFT: Keys.ARROW_RIGHT, Keys.ARROW_RIGHT: Keys.ARROW_LEFT}
FOLDERS = ['screenshot', 'debug']
RESET_PATIENCE = 10
LOG_NOT_FOUND_PATIENCE = 40

class LF2Environment():
    def __init__(self, path, ip, port, driverType, characters, difficulty, background, versusPlayer, duel, rewardList, localDriver, headless, canvasSize, debug):
        print('Creating LF2 environment...')

        global FOLDERS
        FOLDERS = [join(path, folder) for folder in FOLDERS]
        for folder in FOLDERS:
            if not exists(folder):
                mkdir(folder)

        self.path = path
        self.url = 'http://' + ip + ':' + str(port)
        self.driverType = driverType
        self.characters = characters
        self.difficulty = difficulty
        self.background = background
        self.versusPlayer = versusPlayer
        self.duel = duel
        self.rewardList = rewardList
        self.localDriver = localDriver
        self.headless = headless
        self.canvasSize = canvasSize
        self.debugMode = debug

        self.action_space = config.ActionSpace(1)
        self.action_space_2 = config.ActionSpace(2)
        self.observation_space = config.ObservationSpace((160, 380))

        self.dir_keys = {'w': False, 'd': False, 'x': False, 'a': False}
        self.dir_keys_2 = {Keys.ARROW_UP: False, Keys.ARROW_DOWN: False, 
                           Keys.ARROW_LEFT: False, Keys.ARROW_RIGHT: False}
        self.log = {}
        self.recording = False
        self.recorder = Recorder()
        self.screenshotting = False
        self.screenshot_index = 0
        self.canvas = None
        self.gameID = None
        self.log_not_found_count = 0

        global REWARD_HP_FACTOR, REWARD_MP_FACTOR
        REWARD_HP_FACTOR = [0] * len(self.characters)
        REWARD_MP_FACTOR = [0] * len(self.characters)
        self.hps = [NOTSET] * len(self.characters)
        self.mps = [NOTSET] * len(self.characters)
        self.init_dicts()

        self.driver = None
        self.figures = {}
        self.axs = {}
        self.ims = {}

        if self.driverType == config.WebDriver.PhantomJS:
            self.get_screenshot = self.get_screenshot_PhantomJS
        else:
            self.get_screenshot = self.get_screenshot_browsers
        if self.duel:
            self.step = self.step_2
        else:
            self.step = self.step_1

        atexit.register(self.close)
        # signal.signal(signal.SIGINT, self.signal_term_handler)
        signal.signal(signal.SIGTERM, self.signal_term_handler)

        self.driver = self.connect(self.url)

    def init_dicts(self):
        if all(f == 0 for f in REWARD_HP_FACTOR):
            REWARD_HP_FACTOR[0] = -1
            for i in range(1, len(REWARD_HP_FACTOR)): REWARD_HP_FACTOR[i] = +1
        if all(f == 0 for f in REWARD_MP_FACTOR):
            REWARD_MP_FACTOR[0] = -1
            for i in range(1, len(REWARD_MP_FACTOR)): REWARD_MP_FACTOR[i] = 0
        self.hps = [NOTSET] * len(self.hps)
        self.mps = [NOTSET] * len(self.mps)

    def connect(self, url):
        if self.driver is not None:
            print('Closing the current driver...')
            self.close()
            sleep(SLEEP_DURATION)
        print('Starting a web driver...')
        driver = seleniumdriver.get(self.driverType, self.localDriver, self.headless, self.path)
        print('Connecting to game server [{0}]...'.format(url))
        driver.get('{0}/game/game.html'.format(url))
        return driver

    def start_game(self):
        started = False
        while not started:
            if self.driver.execute_script('return window.manager == undefined;'):
                print('Page "game.html" is not ready... sleep...')
                sleep(SLEEP_DURATION)
                continue
            try:
                self.driver.execute_script('window.manager.start_game();')
                started = True
            except WebDriverException as e:
                print('WebDriverException: %s' % e)
                self.driver = self.connect(self.url)
                print('Reseting...')
                self.reset()

    def quick_start(self):
        if len(self.characters) > 8: lf2raise('Number of characters [%d] exceed 8.' % len(self.characters))
        if any(ch not in config.Character for ch in self.characters): lf2raise('Character [%s] is not in the role list.' % ch)
        if self.difficulty not in config.Difficulty: lf2raise('Difficulty [%s] is not in the difficulty list.' % self.difficulty)
        if self.background not in config.Background: lf2raise('Background [%s] is not in the bg list.' % self.background)

        num_ai = len(self.characters) - 1
        action_sequence = []
        enemy_start_index = 1
        action_sequence += ['s'] + ['d'] * int(self.characters[0]) + ['s', 'd']
        if self.versusPlayer or self.duel:
            enemy_start_index = 2
            self.perform_actions(action_sequence, pause=False)
            action_sequence = []
            sleep(SLEEP_DURATION)
            action_sequence += ['j'] + [Keys.ARROW_RIGHT] * int(self.characters[1]) + ['j', Keys.ARROW_RIGHT, Keys.ARROW_RIGHT, 'j']
            self.perform_actions(action_sequence, pause=False)
            action_sequence = []
            sleep(SLEEP_DURATION)
        action_sequence += ['s']
        action_sequence += ['d'] * (num_ai-1) + ['s']
        for b in self.characters[enemy_start_index:]:
            action_sequence += ['a'] * int(self.difficulty) + ['s'] + ['d'] * int(b) + ['s', 'd', 'd', 's']
        action_sequence += ['x', 'x', 'x'] + ['d'] * int(self.background) + ['w', 'w', 'w', 's']
        if not self.versusPlayer or self.duel:
            action_sequence += [Keys.F2]
        self.perform_actions(action_sequence, pause=False)

        self.canvas = self.driver.find_element_by_id('canvas')

    def perform_actions(self, actions, delay=0, pause=True):
        action_chains = ActionChains(self.driver)
        if pause:
            action_chains.key_down(Keys.F2)
        for action in actions:
            action_chains.key_down(action)
        if pause:
            for _ in range(delay):
                action_chains.key_down(Keys.F2)
        action_chains.perform()

    def perform_actions_2(self, actions, delay=0, pause=True):
        action_chains = ActionChains(self.driver)

        if actions == []:
            self.release_all_keys()
        for action in actions:
            action_chains.key_down(action)

        if pause:
            action_chains.send_keys(Keys.F2)
            for _ in range(delay):
                action_chains.send_keys(Keys.F2)

        action_chains.perform()

    def perform_actions_2_2(self, actions, delay=0, pause=True):
        action_chains = ActionChains(self.driver)

        if actions == []:
            self.release_all_keys_2()
        for action in actions:
            action_chains.key_down(action)

        if pause:
            action_chains.send_keys(Keys.F2)
            for _ in range(delay):
                action_chains.send_keys(Keys.F2)

        action_chains.perform()

    def perform_actions_3(self, actions, delay=0, pause=True):
        action_chains = ActionChains(self.driver)

        for key, flag in self.dir_keys.items():
            if flag:
                if key not in actions:
                    self.keyup(key)
            else:
                if key in actions:
                    self.keydown(key)

        if pause:
            action_chains.send_keys(Keys.F2)
            for _ in range(delay):
                action_chains.send_keys(Keys.F2)

        action_chains.perform()

    def perform_actions_3_2(self, actions, delay=0, pause=True):
        action_chains = ActionChains(self.driver)

        for key, flag in self.dir_keys_2.items():
            if flag:
                if key not in actions:
                    self.keyup_2(key)
            else:
                if key in actions:
                    self.keydown_2(key)

        if pause:
            action_chains.send_keys(Keys.F2)
            for _ in range(delay):
                action_chains.send_keys(Keys.F2)

        action_chains.perform()

    def idle(self, delay=0):
        self.perform_actions([], delay)

    def allDirections(self, step_action):
        return (step_action>=1 and step_action<=4) or (step_action>=10 and step_action<=13)

    def keydown(self, key):
        self.release_opposite_key(key)
        self.driver.execute_script('window.myKeyDown(%d);' % config.keyCode[key])
        self.dir_keys[key] = True

    def keyup(self, key):
        self.driver.execute_script('window.myKeyUp(%d);' % config.keyCode[key])
        self.dir_keys[key] = False

    def keydown_2(self, key):
        self.release_opposite_key_2(key)
        self.driver.execute_script('window.myKeyDown(%d);' % config.keyCode[key])
        self.dir_keys_2[key] = True

    def keyup_2(self, key):
        self.driver.execute_script('window.myKeyUp(%d);' % config.keyCode[key])
        self.dir_keys_2[key] = False

    def release_all_keys(self):
        for key, flag in self.dir_keys.items():
            if flag:
                self.keyup(key)

    def release_all_keys_2(self):
        for key, flag in self.dir_keys_2.items():
            if flag:
                self.keyup_2(key)

    def release_opposite_key(self, key):
        if key not in OPPOSITE_KEYS:
            return
        op = OPPOSITE_KEYS[key]
        if self.dir_keys[op]:
            self.keyup(op)

    def release_opposite_key_2(self, key):
        if key not in OPPOSITE_KEYS:
            return
        op = OPPOSITE_KEYS[key]
        if self.dir_keys_2[op]:
            self.keyup_2(op)

    def crop(self, i):
        upper_bound = 150
        return i[upper_bound:upper_bound+334, :, :]

    def get_screenshot_PhantomJS(self):
        # Original method for phantomjs
        image = self.driver.get_screenshot_as_base64()
        i = png2rgb(image)
        return i
        # # Slower method
        # image = self.driver.get_screenshot_as_png()
        # i = io.BytesIO(image)
        # i = mpimg.imread(i, format='PNG')
        # return i

    def get_screenshot_browsers(self):
        # Efficient method for ChromeDriver
        # self.canvas = self.driver.find_element_by_id('canvas')
        image = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", self.canvas)
        i = png2rgb(image)
        return i

    def get_cropped_screenshot(self):
        i = self.get_screenshot()
        if self.driverType == config.WebDriver.PhantomJS:
            i = i[80:240, 10:390, :] # 160x380x3
        else:
            if self.canvasSize != i.shape[0:2]:
                print('Warning: the screenshot size is (%d, %d) rather than (%d, %d).' % (i.shape[0], i.shape[1], self.canvasSize[0], self.canvasSize[1]))
            i = self.crop(i)
            i = imresize(i, (160, 380), interp='bilinear')
        return i
        
    def get_observation(self):
        return rgb2gray(self.get_cropped_screenshot())
    
    def get_log(self):
        return self.driver.execute_script('return window.my_msg;')
        # return self.driver.get_log('browser')
        
    def get_gameID(self):
        return self.driver.execute_script('return window.gameID;')
    
    def get_framecount(self):
        return self.driver.execute_script('return window.framecount;')
    
    def set_ai_epsilon(self, ai_epsilon):
        return self.driver.execute_script('window.epsilon = ' + str(ai_epsilon) + ';')
    
    def set_hp_full(self, value):
        return self.driver.execute_script('GC.default.health.hp_full = ' + str(value) + ';')
    
    def set_mp_full(self, value):
        return self.driver.execute_script('GC.default.health.mp_full = ' + str(value) + ';')
    
    def set_mp_start(self, value):
        print()
        return self.driver.execute_script('GC.default.health.mp_start = ' + str(value) + ';')

    def get_saved_log(self):
        return self.log

    def get_reset_options(self):
        return {'ai_epsilon': None, 'hp_full': 500, 'mp_full': 500, 'mp_start': 500}

    def reset(self, options=None):
        self.driver.refresh()
        self.init_dicts()
        self.dir_keys = {'w': False, 'd': False, 'x': False, 'a': False}

        sleep(SLEEP_DURATION)

        if options is not None:
            if options['ai_epsilon'] is not None:
                self.set_ai_epsilon(options['ai_epsilon'])
            if options['hp_full'] is not None:
                self.set_hp_full(options['hp_full'])
            if options['mp_full'] is not None:
                self.set_mp_full(options['mp_full'])
            if options['mp_start'] is not None:
                self.set_mp_start(options['mp_start'])

        self.start_game()
        self.quick_start()
        sleep(SLEEP_DURATION)

        new_gameID = self.get_gameID()
        load_count = 0
        while new_gameID is None or new_gameID == 'None' or new_gameID == 'not_assign' or new_gameID == self.gameID:
            print('reset(): Not refresh yet! new_gameID is %s. So sleep for %d seconds.' % (new_gameID, SLEEP_DURATION))
            sleep(SLEEP_DURATION)
            new_gameID = self.get_gameID()
            load_count += 1
            if load_count >= RESET_PATIENCE:
                self.driver = self.connect(self.url)
                return self.reset()
        self.log = self.get_log()
        self.gameID = new_gameID
        print('reset(): after reset, gameID: %s, log: %s.' % (self.gameID, self.log))

        observation = self.get_observation()
        return observation

    def step_action(self, action, pause=True):
        if self.allDirections(action):
            self.perform_actions_3(self.action_space.get(action), pause=pause)
        else:
            self.perform_actions_2(self.action_space.get(action), pause=pause)

    def step_action_2(self, action, pause=True):
        if self.allDirections(action):
            self.perform_actions_3_2(self.action_space_2.get(action), pause=pause)
        else:
            self.perform_actions_2_2(self.action_space_2.get(action), pause=pause)

    def step_log(self):
        reward, done, info = 0, False, False
        reward_hp = reward_mp = 0

        log = self.get_log()
        self.log = log
        if log == None or log == 'None':
            self.log_not_found_count += 1
            print('Log Not Found Error: cannot find any log by executing scripts.')
            if self.log_not_found_count >= LOG_NOT_FOUND_PATIENCE:
                print('step(): restart the web driver and reset env because log not found more than %d times.' % LOG_NOT_FOUND_PATIENCE)
                self.driver = self.connect(self.url)
                self.reset()
                done = True
        elif log == 'gameover':
            self.log_not_found_count = 0
            done = True
            print('step(): log == "gameover"')
            info = True
        else:
            self.log_not_found_count = 0
            done = False
            try:
                content = json.loads(log)
                for idx, character in enumerate(content):
                    name = character['name']
                    if 'hp' in self.rewardList and self.hps[idx] != NOTSET:
                        reward_hp += (self.hps[idx] - character['health']['hp']) * REWARD_HP_FACTOR[idx]
                    self.hps[idx] = character['health']['hp']
                    if 'mp' in self.rewardList and self.mps[idx] != NOTSET:
                        reward_mp += (self.mps[idx] - character['health']['mp']) * REWARD_MP_FACTOR[idx]
                    self.mps[idx] = character['health']['mp']
                info = True
            except ValueError as error:
                print('JSON Error: %s. Log: %s. Saved log: %s.' % (error, log, self.get_saved_log()))
                self.debug('error')

        reward = reward_hp / 40.0 + reward_mp / 400 # clips reward
        return reward, done, info

    def step_obsv(self):
        observation = self.get_observation()
        if self.recording:
            self.recorder.add(self.get_screenshot())
        if self.screenshotting:
            self.render_save('%d.png' % self.screenshot_index)
            self.screenshot_index += 1
        return observation

    def step_1(self, action):
        self.step_action(action, pause=(not self.versusPlayer))
        return (self.step_obsv(), ) + self.step_log()

    def step_2(self, action, action2):
        self.step_action(action, pause=False)
        self.step_action_2(action2, pause=True)
        return (self.step_obsv(), ) + self.step_log()

    def debug(self, name):
        self.render_save('%s_orig.png' % name, 'orig', (400, 300), 'debug')
        self.render_save('%s_crop.png' % name, 'crop', (380, 160), 'debug')
        self.render_save('%s_obsv.png' % name, 'obsv', (380, 160), 'debug')
        with open(join(self.path, 'debug', '%s.log' % name), 'w') as f:
            f.write(json.dumps(self.get_saved_log()))

    def get_detail(self):
        try:
            content = json.loads(self.log)
            if len(content) == 0:
                print('get_detail(): len(json.loads(self.log)) == 0')
                return None
        except:
            print('get_detail(): log %s' % self.log)
            return None

        detail = [{}] * len(self.characters)
        for idx, character in enumerate(content):
            name = character['name']
            detail[idx] = {}
            detail[idx]['name'] = name
            detail[idx]['hp'] = character['health']['hp']
            detail[idx]['mp'] = character['health']['mp']
            detail[idx]['x'] = character['ps']['x']
            detail[idx]['y'] = character['ps']['y']
            detail[idx]['z'] = character['ps']['z']
            detail[idx]['vx'] = character['ps']['vx']
            detail[idx]['vy'] = character['ps']['vy']
            detail[idx]['vz'] = character['ps']['vz']
            detail[idx]['pose'] = character['frame']['D']['name']
            detail[idx]['mp'] = character['health']['mp']
        return detail

    def plot(self, data, label=None, index=0):
        from matplotlib import pyplot as plt
        if index not in plt.get_fignums():
            data = np.zeros((300, 400, 3))
            plt.ion()
            self.figures[index] = plt.figure(index)
            self.axs[index] = self.figures[index].add_subplot(1, 1, 1)
            if not self.debugMode:
                self.axs[index].axis('off')
            self.ims[index] = self.axs[index].imshow(data)
        self.ims[index].set_data(data)
        if label is not None:
            self.axs[index].set_title(label)
        self.figures[index].canvas.draw()
        # plt.pause(0.005)

    def render(self, label=None):
        obsv = self.get_screenshot()
        self.plot(obsv, label, index=0)

    def render_out(self, label=None):
        obsv = np.zeros((300, 400))
        obsv[80:240, 10:390] = self.get_observation()
        obsv = np.stack([obsv, obsv, obsv], axis=2)
        self.plot(obsv, label, index=1)

    def render_save(self, name='save.png', type='orig', size=(400, 300), path='screenshot'):    # type 'orig', 'crop', 'obsv'
        obsv = None
        if type == 'orig':
            if self.driverType != config.WebDriver.PhantomJS:
                return
            obsv = self.get_screenshot()
        elif type == 'crop':
            obsv = self.get_cropped_screenshot()
            if obsv.shape[2] == 3:
                obsv = np.stack([obsv[:,:,0], obsv[:,:,1], obsv[:,:,2], (np.ones_like(obsv[:,:,0])*255).astype(np.uint8)], axis=2)
        elif type == 'obsv':
            obsv = self.get_observation()
            obsv = np.stack([obsv, obsv, obsv, (np.ones_like(obsv)*255).astype(np.uint8)], axis=2)
        im = Image.new('RGBA', size)
        # print(obsv.shape)
        im.paste(Image.fromarray(obsv, "RGBA"), (0, 0))
        im.save(join(self.path, path, name))

    def start_recording(self):
        if not self.recording: self.recording= True
        else: print('Already started recording that screen.')

    def stop_recording(self):
        if self.recording: self.recording = False
        else: print('Already stopped recording that screen.')

    def save_recording(self, filename, delete_after_saved=True):
        self.recorder.save(filename)
        if delete_after_saved: self.recorder.clear()

    def close(self):
        if self.driver is not None:
            self.driver.service.process.send_signal(signal.SIGTERM) # kill the specific phantomjs child proc
            self.driver.quit()                                      # quit the node proc
            self.driver = None
            print('Web driver is closed.')
        print('Env closed.')

    def signal_term_handler(self, signal, frame):
        print('W: interrupt received, stopping…')
        self.close()
        # sys.exit(0)

    def start_screenshotting(self):
        self.screenshotting = True
        self.screenshot_index = 0

    def stop_screenshotting(self):
        self.screenshotting = False
