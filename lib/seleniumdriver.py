#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

from .lf2exception import lf2raise

import platform
from os.path import join
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def get(driverType, localDriver, path='.'):
    driverType = str(driverType)
    if driverType == 'PhantomJS':
        # phantomjs_options.add_argument("--disable-web-security")
        if localDriver:
            source = get_source(driverType, path)
            # driver = webdriver.PhantomJS(executable_path=source, service_log_path='log/ghostdriver.log', service_args=["--remote-debugger-port=9000", "--web-security=false"])
            driver = webdriver.PhantomJS(executable_path=source, service_args=["--remote-debugger-port=9000", "--web-security=false"])
        else:
            # driver = webdriver.PhantomJS(service_log_path='log/ghostdriver.log', service_args=["--remote-debugger-port=9000", "--web-security=false"])
            driver = webdriver.PhantomJS(service_args=["--remote-debugger-port=9000", "--web-security=false"])
    elif driverType == 'Chrome':
        desired = DesiredCapabilities.CHROME
        desired['loggingPrefs'] = {'browser': 'ALL'}
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-web-security")
        # chrome_options.add_argument("--window-size=800,600")
        # chrome_options.add_argument("--headless") # will not show the Chrome browser window
        if localDriver:
            source = get_source(driverType, path)
            driver = webdriver.Chrome(executable_path=source, desired_capabilities=desired, chrome_options=chrome_options)
        else:
            driver = webdriver.Chrome(desired_capabilities=desired, chrome_options=chrome_options)
    elif driverType == 'Firefox':
        # desired = DesiredCapabilities.FIREFOX
        # desired['loggingPrefs'] = {'browser': 'ALL'}
        firefox_options = Options()
        firefox_options.add_argument("--start-maximized")
        firefox_options.add_argument("--disable-infobars")
        if localDriver:
            source = get_source(driverType, path)
            driver = webdriver.Firefox(executable_path=source, firefox_options=firefox_options)
        else:
            driver = webdriver.Firefox(firefox_options=firefox_options)
    return driver

def get_source(driverType, path='.'):
    driverType = str(driverType)
    os = platform.system()
    bits = platform.architecture()[0]
    source = None
    if driverType == 'PhantomJS':
        if os == 'Windows':
            source = join(path, 'webdriver/phantomjsdriver_2.1.1_win32/phantomjs.exe')
        elif os == 'Darwin':
            source = join(path, 'webdriver/phantomjsdriver_2.1.1_mac64/phantomjs')
        elif os == 'Linux' and bits == '32bit':
            source = join(path, 'webdriver/phantomjsdriver_2.1.1_linux32/phantomjs')
        elif os == 'Linux' and bits == '64bit':
            source = join(path, 'webdriver/phantomjsdriver_2.1.1_linux64/phantomjs')
        else:
            lf2raise('Failed to recognize your OS [%s / %s].' % (os, bits))
    elif driverType == 'Chrome':
        if os == 'Windows':
            source = join(path, 'webdriver/chromedriver_2.35_win32/chromedriver.exe')
        elif os == 'Darwin':
            source = join(path, 'webdriver/chromedriver_2.35_mac64/chromedriver')
        elif os == 'Linux':
            source = join(path, 'webdriver/chromedriver_2.35_linux64/chromedriver')
        else:
            lf2raise('Failed to recognize your OS [%s / %s].' % (os, bits))
    elif driverType == 'Firefox':
        if os == 'Windows' and bits == '32bit':
            source = join(path, 'webdriver/geckodriver_0.19.1_win32/geckodriver.exe')
        elif os == 'Windows' and bits == '64bit':
            source = join(path, 'webdriver/geckodriver_0.19.1_win64/geckodriver.exe')
        elif os == 'Darwin':
            source = join(path, 'webdriver/geckodriver_0.19.1_macos/geckodriver')
        elif os == 'Linux' and bits == '32bit':
            source = join(path, 'webdriver/geckodriver_0.19.1_linux32/geckodriver')
        elif os == 'Linux' and bits == '64bit':
            source = join(path, 'webdriver/geckodriver_0.19.1_linux64/geckodriver')
        else:
            lf2raise('Failed to recognize your OS [%s / %s].' % (os, bits))
    else:
        lf2raise('Not supported driver type [%s].' % driverType)
    return source
