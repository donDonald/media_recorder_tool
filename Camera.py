#!/usr/bin/env python

import argparse
import cv2




def eprint(*_args, **_kwargs):
        print(*_args, file=sys.stderr, **_kwargs)




class Camera:




        class Config:


                def __init__(self, args):
                        self._verbosity = args.verbosity
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


        def __init__(self, config):
                self._config = config
                pass


        def list(config):
                result = []
                # Checks the first 10 indexes.
                index = 0
                i = 10
                while i > 0:
                        cap = cv2.VideoCapture(index)
                        if cap.read()[0]:
                                result.append((index, f"camera-{index}"))
                                if config.verbosity > 1:
                                        print(f"ID:{index}")
                                        print(f"Name:camera-{index}")
                                cap.release()
                        index += 1
                        i -= 1
                return result


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
                        cv2.imshow(f"camera-{self._config.device}", img)
                        cv2.namedWindow(f"camera-{self._config.device}", cv2.WINDOW_NORMAL)
                        cv2.resizeWindow(f"camera-{self._config.device}", width, height)
                        if cv2.waitKey(1) == 27: 
                                break  # esc to quit
                cv2.destroyAllWindows()




def main():
        # Create arguments parser
        example = "./Camera.py -v1 --device=0"
        parser = argparse.ArgumentParser(prog='Camera',
                                         description='Display a video from a camera',
                                         epilog=example)

        parser.add_argument("--verbosity", "-v", type=int, choices=[0, 1, 2], default=0, help="set verbosity level")
        parser.add_argument("--device", "-d", type=int, default=0, help="set video capture device(default: 0)")
        args = parser.parse_args()

        # Create configuration
        config = Camera.Config(args)

        # List available camera devices
        print("==========================================================")
        devices = Camera.list(config)
        print("Available camera devices:")
        if devices:
                for device in devices:
                        print(f"- device ID: {device[0]}, name:{device[1]}")
        else:
                print("No camera devices found.")
                sys.exit(0)

        # Create camera
        camera = Camera(config)
        camera.show(mirror=True)




if __name__ == '__main__':
        main()
