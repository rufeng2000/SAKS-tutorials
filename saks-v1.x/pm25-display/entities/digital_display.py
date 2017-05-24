#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 NXEZ.COM.
# http://www.nxez.com
#
# Licensed under the GNU General Public License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.gnu.org/licenses/gpl-2.0.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Spoony'
__version__  = 'version 0.0.1'
__license__  = 'Copyright (c) 2015 NXEZ.COM'

import RPi.GPIO as GPIO
import time
import re
from threading import Thread

class DigitalDisplay(object):
    '''
    Digital display class
    '''
    __pins = {'seg':[], 'sel':[]}
    __real_true = GPIO.HIGH
    __numbers = ''
    __is_flushing = False
    __number_code = [0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f, 0x00]
    __pin_stat = {}

    def __init__(self, pins, real_true = GPIO.HIGH):
        '''
        Init the digital display
        :param pin: pin numbers in array
        :param real_true: GPIO.HIGH or GPIO.LOW
        :return: void
        '''
        self.__pattern = re.compile(r'[#| |\d]\.?')
        self.__pins = pins
        self.__real_true = real_true
        self.__pin_stat = { pin : True for pin in self.__pins['sel'] + self.__pins['seg'] }
        self.off()
        try:
            t1 = Thread(target = self.flush_4bit)
            t1.setDaemon(True)
            t1.start()
        except:
            print "Error: Unable to start thread by DigitalDisplay"

    @property
    def numbers(self):
        '''
        Get the current numbers array showing
        :return: numbers array
        '''
        return self.__numbers

    def on(self):
        '''
        Set display on
        :return: void
        '''
        self.__is_flushing = True

    def off(self):
        '''
        Set display off
        :return: void
        '''
        self.__is_flushing = False

    def show(self, str):
        '''
        Set the numbers array to show and enable the display
        :return: void
        '''
        self.__numbers = str

    def set_pin(self, pin, v):
        '''
        Fixed by wyb, for better display.
        '''
        if v != self.__pin_stat[pin]:
            self.__pin_stat[pin] = v
            GPIO.output(pin, not self.__real_true if v else self.__real_true)
    
    def flush_bit(self, sel, num, dp):
        try:
            n = self.__number_code[int(num)]
        except:
            self.set_pin(self.__pins['sel'][sel], False)
            return

        if dp:
            n |= 0x80

        j = 4
        for i in range(8):
            pin = self.__pins['seg'][i]
            v = ((n & (1 << i)) != 0)
            if v != self.__pin_stat[pin]:
                for k in range(j):
                    if k != sel:
                        self.set_pin(self.__pins['sel'][k], False)
                j = 0
                self.set_pin(pin, v)

        self.set_pin(self.__pins['sel'][sel], True)

    def flush_4bit(self):
        number = ''
        digits = []
        while True:
            if self.__is_flushing:
                if number != self.__number:
                    number = self.__number
                    matches = self.__pattern.findall(number)
                    digits = []
                    for i in range(len(matches)):
                        digits.append((matches[i].replace('.',''), matches[i].count('.') > 0))
                for i in range(min(4, len(digits))):
                    self.flush_bit(i, *digits[i])
                    time.sleep(0.005)
            else:
                for pin in self.__pins['sel']:
                    self.set_pin(pin, False)
                time.sleep(0.02)
