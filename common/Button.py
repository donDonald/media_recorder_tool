#!/usr/bin/env python

import os
import sys
import argparse
import cv2
#import ffmpeg # https://kkroening.github.io/ffmpeg-python/
import numpy as np
import pyaudio
import subprocess as sp
import time




def eprint(*_args, **_kwargs):
        print(*_args, file=sys.stderr, **_kwargs)




class Button:


        def __init__(self, x:int, y:int, off_on):
                self._state = False
                self._x = x
                self._y = y

                self._off, self._on = off_on
                image_on = self._on[0]
                self._image_on = cv2.imread(image_on)
                height_on, width_on, channels_on = self._image_on.shape
                image_off = self._off[0]
                self._image_off = cv2.imread(image_off)
                height_off, width_off, channels_off = self._image_off.shape

                width = max([width_on, width_off])
                height = max([height_on, height_off])

                self._w = width
                self._h = height

                self._left = x
                self._top  = y
                self._right  = x + width - 1 
                self._bottom = y + height - 1
                self._text = self._off[1]
                pass


        #@model.getter
        @property
        def state(self):
                return self._state


        def set(self, state:bool):
                self._state = state
                self._color = self._on[0] if self._state else self._off[0]
                self._text  = self._on[1] if self._state else self._off[1]
                pass


        def toggle(self):
                self._state = not self._state
                self._color = self._on[0] if self._state else self._off[0]
                self._text  = self._on[1] if self._state else self._off[1]
                pass


        def draw(self, img):
                # Draw image
                btn = self._image_on if self._state else self._image_off
                x_offset = self._x;
                y_offset = self._y;
                img[y_offset:y_offset+btn.shape[0], x_offset:x_offset+btn.shape[1]] = btn

                # Draw text
                if len(self._text):
                        fontFace = cv2.FONT_HERSHEY_PLAIN
                        fontScale = 1.0
                        thickness = 2

                        ((fw,fh), baseline) = cv2.getTextSize(
                                "", fontFace=fontFace, fontScale=fontScale, thickness=thickness) # empty string is good enough

                        height_in_pixels = btn.shape[0]
                        fontScale = height_in_pixels/fh

                        org = (x_offset + btn.shape[1] + int(50*btn.shape[1]/100), self._y+height_in_pixels)
                        cv2.putText(
                                img=img, text=self._text, org=org,
                                fontFace=fontFace, fontScale=fontScale, color=(0, 0, 0), thickness=thickness)

                return img


        def handle_event(self, event, x, y, flags, param):
                self._hover = (self._left <= x <= self._right and self._top <= y <= self._bottom)

                if self._hover and flags == 1:
                        pass

               #self.clicked = False
               #print(event, x, y, flags, param)
               #
               #if self.command:
               #    self.command()
