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
# tutorials url: http://shumeipai.nxez.com/2015/05/31/saks-diy-tutorials-website-detection.html

__author__ = 'Spoony'
__license__  = 'Copyright (c) 2015 NXEZ.COM'

import RPi.GPIO as GPIO
import time
import urllib2
import socket

GPIO.setmode(GPIO.BCM)
# 输出模式
GPIO.setup(1, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
# 要检测的网址
url = "http://shumeipai.nxez.com/"
# 设置超时时间10秒
urllib2.socket.setdefaulttimeout(10)
# 初始化状态
status = 0
# 检测频率间隔
interval = 60

def check():
    global status
    try:
        response = urllib2.urlopen(url)
        if response.code == 200:
            status = 200
    except urllib2.HTTPError, e:
        if e.code == 500 or e.code == 404 or e.code == 403:
            status = e.code
        else:
            status = 0
    except urllib2.URLError, e:
        print e
        status = 0
    finally:
        print status


while True:
    check()
    #正常状态，绿灯亮
    if status == 200:
        GPIO.output(1, GPIO.LOW)
        GPIO.output(7, GPIO.HIGH)
        GPIO.output(8, GPIO.HIGH)
    #异常状态，黄灯亮
    elif status == 500 or status == 404 or status == 403:
        GPIO.output(1, GPIO.HIGH)
        GPIO.output(7, GPIO.LOW)
        GPIO.output(8, GPIO.HIGH)
    #错误状态，红灯亮
    else:
        GPIO.output(1, GPIO.HIGH)
        GPIO.output(7, GPIO.HIGH)
        GPIO.output(8, GPIO.LOW)

    time.sleep(interval)