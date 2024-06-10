#!/usr/bin/env python

"""
Simply display the contents of a camera with optional mirroring using OpenCV 
via the new Pythonic cv2 interface. Press <esc> to quit.
"""

import argparse
import cv2




def eprint(*_args, **_kwargs):
        print(*_args, file=sys.stderr, **_kwargs)




class Config:


        def __init__(self, args):
                # Verbosity level
                self._verbosity = args.verbosity

                # Input capture device
                self._device = args.device


        def __str__(self):
                return f"""verbosity:{self.verbosity}
                           device:{self.device}"""


        #@verbosity.getter
        @property
        def verbosity(self):
                return self._verbosity


        #@model.getter
        @property
        def device(self):
                return self._device





class Camera:


        def __init__(self, config):
                self._config = config
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

                while True:
                        ret_val, img = cam.read()
                        if mirror: 
                                img = cv2.flip(img, 1)
                        cv2.imshow('camera', img)
                        cv2.namedWindow('camera', cv2.WINDOW_NORMAL)
                        cv2.resizeWindow('camera', width, height)
                        if cv2.waitKey(1) == 27: 
                                break  # esc to quit
                cv2.destroyAllWindows()




def main():
        # Create arguments parser
        example = "./Camera.py -v1 --device=0"
        parser = argparse.ArgumentParser(prog='Camera',
                                         description='Display a video from a camera',
                                         epilog=example)

        parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0, help="set verbosity level")
        parser.add_argument("--device", type=int, default=0, help="set video capture device(default: 0)")
        args = parser.parse_args()

        # Create configuration
        config = Config(args)
        if config.verbosity > 0:
                print("==========================================================")
                print("config:")
                print(config)


        if config.verbosity > 0:
                print("==========================================================")
                print("available devices:")
                devices = Camera.list()
                if devices:
                        print("Available camera device indices:")
                        for index in devices:
                                print(f"- Device index: {index}")
                else:
                        print("No camera devices found.")

        camera = Camera(config)
        camera.show(mirror=True)




if __name__ == '__main__':
        main()
