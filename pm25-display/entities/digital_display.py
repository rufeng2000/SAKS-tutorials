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
    __number_code = {'0':0x3f, '1':0x06, '2':0x5b, '3':0x4f, '4':0x66, '5':0x6d, '6':0x7d, 
                     '7':0x07, '8':0x7f, '9':0x6f, '-':0x40, '_':0x08, '=':0x48,
                     'A':0x77, 'B':0x7c, 'C':0x39, 'D':0x5e, 'E':0x79, 'F':0x71}
    __pin_stat = {}
    __numbers = ''
    __show = ''

    def __init__(self, pins, real_true = GPIO.HIGH):
        '''
        Init the digital display
        :param pin: pin numbers in array
        :param real_true: GPIO.HIGH or GPIO.LOW
        :return: void
        '''
        self.__pattern = re.compile(r'[-_=A-F0-9 #]\.?')
        self.__pins = pins
        self.__real_true = real_true
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
        self.__numbers = self.__show

    def off(self):
        '''
        Set display off
        :return: void
        '''
        self.__numbers = ''

    def show(self, str):
        '''
        Set the numbers array to show and enable the display
        :return: void
        '''
        self.__numbers = self.__show = str

    def set_pin(self, pin, v):
        if v != self.__pin_stat[pin]:
            self.__pin_stat[pin] = v
            GPIO.output(pin, self.__real_true if v else not self.__real_true)

    def flush_bit(self, sel, num, dp):
        sel_pin = self.__pins['sel'][sel]
        if not num in self.__number_code:
            self.set_pin(sel_pin, False)
            return
        n = self.__number_code[num] | (0x80 if dp else 0x00)
        j = True
        for i in range(8):
            pin = self.__pins['seg'][i]
            v = ((n & (1 << i)) != 0)
            if v != self.__pin_stat[pin]:
                if j:
                    for k in self.__pins['sel']:
                        if k != sel_pin:
                            self.set_pin(k, False)
                    j = False
                self.set_pin(pin, v)
        self.set_pin(sel_pin, True)

    def flush_4bit(self):
        numbers = ''
        digits = []
        for pin in self.__pins['sel'] + self.__pins['seg']:
            self.__pin_stat[pin] = True
            self.set_pin(pin, False)
        while True:
            if numbers != self.__numbers:
                numbers = self.__numbers
                matches = self.__pattern.findall(numbers)
                digits = []
                for i in range(len(matches)):
                    digits.append((matches[i].replace('.',''), matches[i].count('.') > 0))
            if digits:
                for i in range(min(4, len(digits))):
                    self.flush_bit(i, *digits[i])
                    time.sleep(0.005)
            else:
                for pin in self.__pins['sel']:
                    self.set_pin(pin, False)
                time.sleep(0.02)
