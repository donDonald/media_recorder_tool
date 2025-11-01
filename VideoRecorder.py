#!/usr/bin/env python

import os
import sys
import argparse
import cv2
import numpy as np
import ffmpeg # https://kkroening.github.io/ffmpeg-python/
import Button




def eprint(*_args, **_kwargs):
        print(*_args, file=sys.stderr, **_kwargs)




class VideoRecorder:




        class Config:


                def __init__(self, args):
                        self._verbosity = args.verbosity
                        self._device = args.device
                        self._oformat = args.oformat
                        self._owidth = args.owidth
                        self._oheight = args.oheight
                        self._fps = args.fps
                        self._wwidth = args.wwidth
                        self._wheight = args.wheight
                        self._command = args.command
                        self._output = args.output[0] if args.output else ""


                def __str__(self):
                        return f"""verbosity:{self.verbosity}
                                   device:{self.device}
                                   oformat:{self.oformat}
                                   owidht:{self.owidth}
                                   oheight:{self.oheight}
                                   fps:{self.fps}
                                   wwidht:{self.wwidth}
                                   wheight:{self.wheight}
                                   command:{self.command}
                                   output:{self.output}"""


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


                #@model.getter
                @property
                def command(self):
                        return self._command


                #@model.getter
                @property
                def output(self):
                        return self._output




        def __init__(self, config):
                self._config = config
                self._recordButton = Button.Button(10, 10, (("assets/off.png", ""), ("assets/on.png", "Live")))
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

                # FFmpeg output settings
                process = (
                        ffmpeg
                        .input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}', r=FPS)
                        .output(self._config.output, pix_fmt='yuv420p', vcodec='libx264')
                        .overwrite_output()
                        .run_async(pipe_stdin=True)
                )

                # Set initial state
                self._recordButton.set(True if self._config.command == "record" else False)

                try:
                        while True:
                                success, frame = cam.read()
                                if not success:
                                        eprint('Error reading camera, exiting')
                                        sys.exit(1)

                                # Draw record burron
                                frame = self._recordButton.draw(frame)

                                # Scale the image to desired size
                                frame = cv2.resize(frame, OUTPUT_SIZE)

                                if self._recordButton._state:
                                        # Write the frame to FFmpeg's stdin
                                        process.stdin.write(frame.astype(np.uint8).tobytes())

                                # Display the frame
                                cv2.imshow(f"Camera-{self._config.device}", frame)

                                key = cv2.waitKey(1)
                                if key == 27: 
                                        break  # esc to quit
                                elif key == ord('r'):
                                        self._recordButton.toggle()

                except KeyboardInterrupt:
                        print("Stopping capture.")
                finally:
                        # Release resources
                        cam.release()
                        cv2.destroyAllWindows()
                        process.stdin.close()
                        process.wait()
                        print("Video saved as", self._config.output)



# ################################################### OpenCV VideoWriter ##############################################
#                               # Setup video codec
#                               #fourcc = -1
#                               #print(fourcc)
#                               OUTPUT_FORMAT = self._config.oformat
#                               fourcc = cv2.VideoWriter_fourcc(*f'{OUTPUT_FORMAT}')
#                               if self._config.verbosity > 0:
#                                       print("==========================================================")
#                                       print("output:")
#                                       print(f"    output:{self._config.output}")
#                                       print(f"    format:{OUTPUT_FORMAT}")
#                                       print(f"    size:{OUTPUT_SIZE}")
#                                       print(f"    fps:{FPS}")
#                                       print(f"    fourcc:{fourcc}")

#                               # Create output device
#                               output = cv2.VideoWriter(self._config.output, fourcc, FPS, OUTPUT_SIZE)
#                               if output.isOpened():
#                                       if self._config.verbosity > 0:
#                                               print(f'Output is opened')
#                               else:
#                                       eprint('Cant\'t open open output, supported codecs:')
#                                       cv2.VideoWriter(self._config.output, -1, FPS, OUTPUT_SIZE)
#                                       eprint('Cant\'t open open output, exiting')
#                                       sys.exit(1)
#               # https://docs.opencv.org/4.x/d4/d15/group__videoio__flags__base.html#ga41c5cfa7859ae542b71b1d33bbd4d2b4
#               # https://docs.opencv.org/4.x/dc/dfc/group__videoio__flags__others.html
#               # https://stackoverflow.com/questions/59023363/encoding-hevc-video-using-opencv-and-ffmpeg-backend
#               # ffmpeg -encoders


#                               while True:
#                                       success, img = cam.read()
#                                       if not success:
#                                               eprint('Error reading camera, exiting')
#                                               sys.exit(1)

#                                       #if mirror: 
#                                       img = cv2.flip(img, 1)

#                                       cv2.namedWindow('camera', cv2.WINDOW_NORMAL)
#                                       cv2.resizeWindow('camera', WINDOW_WIDTH, WINDOW_HEIGHT)

#                                       img = self._recordButton.draw(img)

#                                       # assign mouse click to method in button instance
#                                       #cv2.setMouseCallback("x", self._recordButton.handle_event)
#                                       #cv2.setMouseCallback("x", Xhandle_event)
#                                       #https://docs.opencv.org/4.x/db/d5b/tutorial_py_mouse_handling.html
#                                       
#                                       cv2.imshow('camera', img)

#                                       # Scale the image to desired size
#                                       img = cv2.resize(img, OUTPUT_SIZE)

#                                       # Write the image tor the output
#                                       if self._recordButton._state:
#                                               output.write(img)
#                                       
#                                       key = cv2.waitKey(1)
#                                       if key == 27: 
#                                               break  # esc to quit
#                                       elif key == ord('r'):
#                                               self._recordButton.toggle()


#                               cam.release()
#                               output.release()
#                               cv2.destroyAllWindows()




def main():
        # Create arguments parser
        example = "./VideoRecorder.py out.avi --device=0 --wwidth=1024 --wheight=800"
        parser = argparse.ArgumentParser(prog='VideoRecorder',
                                         description='Record audio from a camera into a file',
                                         epilog=example)

        parser.add_argument("--verbosity", "-v", type=int, choices=[0, 1, 2], default=0, help="set verbosity level")
        parser.add_argument("--device", "-d", type=int, default=0, help="set video capture device(default: 0)")
        parser.add_argument("--oformat", choices=["MJPG", "FMP4", "mp4v", "XVID", "DIVX", "avc1", "hvc1", "vp09", "hev1"], default="avc1", help="outout fomat or vidoecodec(default: hev11)")
        parser.add_argument("--owidth", type=int, default=-1, help="set output width(default: device width)")
        parser.add_argument("--oheight", type=int, default=-1, help="set output height(default: device height)")
        parser.add_argument("--fps", "-f", type=int, default=15, help="set frames per second(default 15)")
        parser.add_argument("--wwidth", type=int, default=-1, help="set window width(default: device width)")
        parser.add_argument("--wheight", type=int, default=-1, help="set window height(default: device height)")
        parser.add_argument("--command", choices=["pause", "record"], default="pause", help="command to recorder(default: pause)")
       #parser.add_argument('output', type=str, help='Path to output file')
       #args = parser.parse_args()
        parser.add_argument("output", nargs='*', default=argparse.SUPPRESS)
        args = parser.parse_args(namespace=argparse.Namespace(output=None))

        # Create configuration
        config = VideoRecorder.Config(args)

        # List available camera devices
        if not config.output:
                print("==========================================================")
                devices = VideoRecorder.list(config)
                print("Available camera devices:")
                if devices:
                        for device in devices:
                                print(f"- device ID:{device[0]}, name:{device[1]}")
                else:
                        print("No camera devices found.")
                sys.exit(0)

        if config.verbosity > 0:
                print("==========================================================")
                print("config:")
                print(config)

        # Create recorder
        recorder = VideoRecorder(config)
        recorder.show(mirror=True)

        #https://docs.opencv.org/3.4/dd/d43/tutorial_py_video_display.html
        #https://www.youtube.com/watch?v=b7ybCOsgf3E
        #http://arahna.de/opencv-save-video/
        # Drivers are needed. For my Linux machine, I found in the repository. To install codec in Ubuntu need run command: sudo apt-get install ffmpeg x264 libx264-dev 




if __name__ == '__main__':
        main()
