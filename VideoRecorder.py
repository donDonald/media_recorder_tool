#!/usr/bin/env python

"""
Simply display the contents of the webcam with optional mirroring using OpenCV 
via the new Pythonic cv2 interface.  Press <esc> to quit.
"""

import os
import sys
import argparse
import cv2


def eprint(*_args, **_kwargs):
        print(*_args, file=sys.stderr, **_kwargs)




class Config:


        def __init__(self, args):
                # verbosity level
                self._verbosity = args.verbosity

                # Training images and XML files directory
                self._output = args.output
               #if self.verbosity > 0:
               #        print(f'File with assigned model:{self.model}')

               #if not os.path.isfile(self.model):
               #        eprint(f'model "{self.model}" does not exist')
               #        eprint('exiting')
               #        sys.exit(1)


        def __str__(self):
                return f"""
                    verbosity:{self.verbosity}
                    output:{self.output}
                """

        #@verbosity.getter
        @property
        def verbosity(self):
                return self._verbosity


        #@model.getter
        @property
        def output(self):
                return self._output




class Recorder:


        def __init__(self, config):
                self._config = config;
                pass


        def show_webcam(self, mirror=False, width=600, height=600):
                cam = cv2.VideoCapture(0)
                if cam.isOpened():
                        if self._config.verbosity > 0:
                                print(f'Camera is opened')
                else:
                        eprint('Cani\'t open camera, exiting')
                        sys.exit(1)

                while True:
                        ret_val, img = cam.read()
                        if mirror: 
                                img = cv2.flip(img, 1)
                        cv2.imshow('my webcam', img)
                        cv2.namedWindow('my webcam', cv2.WINDOW_NORMAL)
                        cv2.resizeWindow('my webcam', width, height)
                        if cv2.waitKey(1) == 27: 
                                break  # esc to quit

                cv2.destroyAllWindows()




if __name__ == '__main__':

        # Create arguments parser
        parser = argparse.ArgumentParser(prog='VideoRecorder',
                                         description='Record a video from camera into a file',
                                         epilog='TOBEDONE')

        parser.add_argument('output', help='Path to output file')
        parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0, help="set output verbosity level")
        args = parser.parse_args()


        # Create configuration
        config = Config(args)
        print("#############")
        print(config)

        # Create recorder
        recorder = Recorder(config)

        # Do it babe
        recorder.show_webcam(mirror=True)

