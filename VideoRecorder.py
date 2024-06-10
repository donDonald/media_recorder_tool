#!/usr/bin/env python

"""
Simply record the contents of the camera into a file using OpenCV
via the new Pythonic cv2 interface. Press <esc> to quit.
"""

import os
import sys
import argparse
import cv2
import ffmpeg




def eprint(*_args, **_kwargs):
        print(*_args, file=sys.stderr, **_kwargs)




class Config:


        def __init__(self, args):
                # Verbosity level
                self._verbosity = args.verbosity

                # Input capture device
                self._device = args.device

                # Output file
                self._output = args.output

                # Output file format(video codec)
                self._oformat = args.oformat

                # Width of the output
                self._owidth = args.owidth

                # Height of the output
                self._oheight = args.oheight

                # FPS
                self._fps = args.fps

                # Width of the window
                self._wwidth = args.wwidth

                # Height of the window
                self._wheight = args.wheight


        def __str__(self):
                return f"""verbosity:{self.verbosity}
                           device:{self.device}
                           output:{self.output}
                           oformat:{self.oformat}
                           owidht:{self.owidth}
                           oheight:{self.oheight}
                           fps:{self.fps}
                           wwidht:{self.wwidth}
                           wheight:{self.wheight}"""


        #@verbosity.getter
        @property
        def verbosity(self):
                return self._verbosity


        #@model.getter
        @property
        def device(self):
                return self._device


        #@model.getter
        @property
        def output(self):
                return self._output


        #@model.getter
        @property
        def oformat(self):
                return self._oformat


        #@model.getter
        @property
        def owidth(self):
                return self._owidth


        #@model.getter
        @property
        def oheight(self):
                return self._oheight


        #@model.getter
        @property
        def fps(self):
                return self._fps


        #@model.getter
        @property
        def wwidth(self):
                return self._wwidth


        #@model.getter
        @property
        def wheight(self):
                return self._wheight




class VideoRecorder:


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


                def toggle(self):
                        self._state = not self._state
                        self._color = self._on[0] if self._state else self._off[0]
                        self._text  = self._on[1] if self._state else self._off[1]
                        pass


                def handle_event(self, event, x, y, flags, param):
                        self._hover = (self._left <= x <= self._right and self._top <= y <= self._bottom)

                        if self._hover and flags == 1:
                                pass

                       #self.clicked = False
                       #print(event, x, y, flags, param)
                       #
                       #if self.command:
                       #    self.command()


        def __init__(self, config):
                self._config = config
                self._recordButton = VideoRecorder.Button(10, 10, (("assets/off.png", ""), ("assets/on.png", "Live")))
                pass


        def list():
                """
                Attempts to open camera devices with increasing indices to identify available cameras.
                """
                # Checks the first 10 indexes.
                index = 0
                arr = []
                i = 10
                while i > 0:
                        cap = cv2.VideoCapture(index)
                        if cap.read()[0]:
                                arr.append(index)
                                cap.release()
                        index += 1
                        i -= 1
                return arr


        def show(self, mirror=False, width=600, height=600):
                cam = cv2.VideoCapture(self._config.device)
                if cam.isOpened():
                        if self._config.verbosity > 0:
                                print(f'Device "{self._config.device}" is opened')
                else:
                        eprint(f'Cant\'t open device "{self._config.device}", exiting')
                        sys.exit(1)

                # Collect device capabilities
                deviceWidth = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
                deviceHeight = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
                deviceFps = cam.get(cv2.CAP_PROP_FPS)
                deviceFrameCount = cam.get(cv2.CAP_PROP_FRAME_COUNT)
                if self._config.verbosity > 0:
                        print("==========================================================")
                        print('device:')
                        print(f'    width:{deviceWidth}')
                        print(f'    height:{deviceHeight}')
                        print(f'    fps:{deviceFps}')
                        print(f'    frame count:{deviceFrameCount}')

                # Setup window size, use device options by default
                WINDOW_WIDTH = self._config.wwidth if (self._config.wwidth > 0) else int(deviceWidth)
                WINDOW_HEIGHT = self._config.wheight if (self._config.wheight > 0) else int(deviceHeight)
                WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
                if self._config.verbosity > 0:
                        print("==========================================================")
                        print("window:")
                        print(f"    size:{WINDOW_SIZE}")

                # Setup output size and fps, use device options by default
                OUTPUT_WIDTH = self._config.owidth if (self._config.owidth > 0) else int(deviceWidth)
                OUTPUT_HEIGHT = self._config.oheight if (self._config.oheight > 0) else int(deviceHeight)
                OUTPUT_SIZE = (OUTPUT_WIDTH, OUTPUT_HEIGHT)
                FPS = self._config.fps if (self._config.fps > 0) else deviceFps

                # Setup video codec
                #fourcc = -1
                #print(fourcc)
                OUTPUT_FORMAT = self._config.oformat
                fourcc = cv2.VideoWriter_fourcc(*f'{OUTPUT_FORMAT}')
                if self._config.verbosity > 0:
                        print("==========================================================")
                        print("output:")
                        print(f"    output:{self._config.output}")
                        print(f"    format:{OUTPUT_FORMAT}")
                        print(f"    size:{OUTPUT_SIZE}")
                        print(f"    fps:{FPS}")
                        print(f"    fourcc:{fourcc}")

                # Create output device
                output = cv2.VideoWriter(self._config.output, fourcc, FPS, OUTPUT_SIZE)
                if output.isOpened():
                        if self._config.verbosity > 0:
                                print(f'Output is opened')
                else:
                        eprint('Cant\'t open open output, supported codecs:')
                        cv2.VideoWriter(self._config.output, -1, FPS, OUTPUT_SIZE)
                        eprint('Cant\'t open open output, exiting')
                        sys.exit(1)
# https://docs.opencv.org/4.x/d4/d15/group__videoio__flags__base.html#ga41c5cfa7859ae542b71b1d33bbd4d2b4
# https://docs.opencv.org/4.x/dc/dfc/group__videoio__flags__others.html
# https://stackoverflow.com/questions/59023363/encoding-hevc-video-using-opencv-and-ffmpeg-backend
# ffmpeg -encoders


                while True:
                        success, img = cam.read()
                        if not success:
                                eprint('Error reading camera, exiting')
                                sys.exit(1)

                        #if mirror: 
                        img = cv2.flip(img, 1)

                        cv2.namedWindow('camera', cv2.WINDOW_NORMAL)
                        cv2.resizeWindow('camera', WINDOW_WIDTH, WINDOW_HEIGHT)

                        img = self._recordButton.draw(img)

                        # assign mouse click to method in button instance
                        #cv2.setMouseCallback("x", self._recordButton.handle_event)
                        #cv2.setMouseCallback("x", Xhandle_event)
                        #https://docs.opencv.org/4.x/db/d5b/tutorial_py_mouse_handling.html
                        
                        cv2.imshow('camera', img)

                        # Scale the image to desired size
                        img = cv2.resize(img, OUTPUT_SIZE)

                        # Write the image tor the output
                        if self._recordButton._state:
                                output.write(img)
                        
                        key = cv2.waitKey(1)
                        if key == 27: 
                                break  # esc to quit
                        elif key == ord('r'):
                                self._recordButton.toggle()


                cam.release()
                output.release()
                cv2.destroyAllWindows()




def main():
        # Create arguments parser
        example = "./VideoRecorder.py out.avi --device=0 --wwidth=1024 --wheight=800"
        parser = argparse.ArgumentParser(prog='VideoRecorder',
                                         description='Record a video from camera into a file',
                                         epilog=example)

        parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0, help="set verbosity level")
        parser.add_argument("--device", type=int, default=0, help="set video capture device(default: 0)")
        parser.add_argument('output', type=str, help='Path to output file')
        parser.add_argument("--oformat", choices=["MJPG", "FMP4", "mp4v", "XVID", "DIVX", "avc1", "hvc1", "vp09", "hev1"], default="avc1", help="outout fomat or vidoecodec(default: avc1)")
        parser.add_argument("--owidth", type=int, default=-1, help="set output width(default: device width)")
        parser.add_argument("--oheight", type=int, default=-1, help="set output height(default: device height)")
        parser.add_argument("-f", "--fps", type=int, default=15, help="set frames per second(default 15)")
        parser.add_argument("--wwidth", type=int, default=-1, help="set window width(default: device width)")
        parser.add_argument("--wheight", type=int, default=-1, help="set window height(default: device height)")
        args = parser.parse_args()


        # Create configuration
        config = Config(args)
        if config.verbosity > 0:
                print("==========================================================")
                print("config:")
                print(config)

        # List available camera devices
        if config.verbosity > 0:
                print("==========================================================")
                print("available devices:")
                devices = VideoRecorder.list()
                if devices:
                        print("Available camera device indices:")
                        for index in devices:
                                print(f"- Device index: {index}")
                else:
                        print("No camera devices found.")

        # Create recorder
        recorder = VideoRecorder(config)
        recorder.show(mirror=True)

        #https://docs.opencv.org/3.4/dd/d43/tutorial_py_video_display.html
        #https://www.youtube.com/watch?v=b7ybCOsgf3E
        #http://arahna.de/opencv-save-video/
        # Drivers are needed. For my Linux machine, I found in the repository. To install codec in Ubuntu need run command: sudo apt-get install ffmpeg x264 libx264-dev 




if __name__ == '__main__':
        main()
