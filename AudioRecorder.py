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
import Button




def eprint(*_args, **_kwargs):
        print(*_args, file=sys.stderr, **_kwargs)




class AudioRecorder:




        class Config:


                def __init__(self, args):
                        self._verbosity = args.verbosity
                        self._device = args.device
                        self._channels = args.channels
                        self._rate = args.rate
                        self._command = args.command
                        self._output = args.output[0] if args.output else ""


                def __str__(self):
                        return f"""verbosity:{self.verbosity}
                                   device:{self.device}
                                   channels:{self.channels}
                                   rate:{self.rate}
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
                def channels(self):
                        return self._channels


                #@model.getter
                @property
                def rate(self):
                        return self._rate


                #@model.getter
                @property
                def output(self):
                        return self._output


                #@model.getter
                @property
                def command(self):
                        return self._command




        def __init__(self, config):
                self._config = config
                self._width = 400;
                self._height = 100;
                self._recordButton = Button.Button(10, 10, (("assets/off.png", ""), ("assets/on.png", "")))
                pass


        def list(config):
                result = []
                p = pyaudio.PyAudio()

                if config.verbosity > 1:
                        print(f"Available Input Devices: {p.get_device_count()}")

                for i in range(p.get_device_count()):
                        device_info = p.get_device_info_by_index(i);
                        if device_info.get('maxInputChannels') > 0:
                                result.append((device_info.get('index'), device_info.get('name')))
                                if config.verbosity > 1:
                                        print(f"ID:{i}")
                                        print(f"Name:{device_info.get('name')}")
                                        print (f"Info:{device_info}")

                p.terminate()
                return result


        def show(self, mirror=False, width=600, height=600):
                # --- Audio settings ---
                FORMAT = pyaudio.paInt16      # 16-bit PCM format
                CHUNK = 1024                  # Frames per buffer

                # --- FFmpeg command for encoding ---
                FFMPEG_BIN = "ffmpeg"
                ffmpeg_command = [
                        FFMPEG_BIN,
                        # Input options for the raw PCM stream from PyAudio
                        '-y',                     # Overwrite output file if it exists
                        '-f', 's16le',            # Raw PCM format (signed 16-bit little-endian)
                        '-acodec', 'pcm_s16le',   # PCM codec for input
                        '-ar', str(self._config.rate),         # Set the audio sample rate
                        '-ac', str(self._config.channels),     # Set the audio channel count
                        '-i', 'pipe:0',           # Read input from stdin (the pipe)
                        # Output options for the encoded file
                        '-vn',                    # Disable video
                        '-acodec', 'libmp3lame',  # Use libmp3lame for MP3 encoding
                        '-f', 'mp3',              # Set output format to MP3
                        self._config.output
                ]


                # --- Main recording process ---
                p = pyaudio.PyAudio()

                # Open the PyAudio input stream
                stream = p.open(
                    format=FORMAT,
                    channels=self._config.channels,
                    rate=self._config.rate,
                    input=True,
                    frames_per_buffer=CHUNK
                )

                # Open the FFmpeg subprocess with stdin connected to a pipe
                ffmpeg_proc = sp.Popen(ffmpeg_command, stdin=sp.PIPE)

                # Draw background
                frame = np.zeros((self._height, self._width, 3), np.uint8)
                cv2.rectangle(frame, (0, 0), (self._width, self._height), (255, 255, 255), -1)

                # Set initial state
                self._recordButton.set(True if self._config.command == "record" else False)

                try:
                        while True:
                                data = stream.read(CHUNK)

                                # Draw record burron
                                frame = self._recordButton.draw(frame)

                                if self._recordButton._state:
                                        # Write the frame to FFmpeg's stdin
                                        ffmpeg_proc.stdin.write(data)

                                # Draw output
                                if len(self._config.output):
                                        fontFace = cv2.FONT_HERSHEY_PLAIN
                                        fontScale = 1.0
                                        thickness = 2

                                        ((fw,fh), baseline) = cv2.getTextSize(
                                                "Y", fontFace=fontFace, fontScale=fontScale, thickness=thickness)

                                        height_in_pixels = self._height/4
                                        fontScale = height_in_pixels/fh
                                        org = (10, self._recordButton._h + 2*int(fontScale*fh))
                                        cv2.putText(
                                                img=frame, text=self._config.output, org=org,
                                                fontFace=fontFace, fontScale=fontScale, color=(0, 0, 0), thickness=thickness)

                                cv2.imshow(f"Microphone-{self._config.device}", frame)

                                key = cv2.waitKey(1)
                                if key == 27: 
                                        break  # esc to quit
                                elif key == ord('r'):
                                        self._recordButton.toggle()
                except KeyboardInterrupt:
                        print("Stopping capture.")
                finally:
                        # Release resources
                        stream.stop_stream()
                        stream.close()
                        p.terminate()

                        # Close the pipe to FFmpeg and wait for it to finish
                        ffmpeg_proc.stdin.close()
                        ffmpeg_proc.wait()
                        print("Audio saved as", self._config.output)
                pass




def main():
        # Create arguments parser
        example = "./AudioRecorder.py --device=0 out.mp3"
        parser = argparse.ArgumentParser(prog='AUdioRecorder',
                                         description='Record audio from a microphone into a file',
                                         epilog=example)

        parser.add_argument("--verbosity", "-v", type=int, choices=[0, 1, 2], default=0, help="set verbosity level")
        parser.add_argument("--device", "-d", type=int, default=0, help="set audio capture device(default: 0)")
        parser.add_argument("--channels", "-c", type=int, default=1, help="set audio channels(default 1)")
        parser.add_argument("--rate", "-r", type=int, default=44100, help="set bit-rate(default 44100)")
        parser.add_argument("--command", choices=["pause", "record"], default="pause", help="command to recorder(default: pause)")
       #parser.add_argument('output', type=str, help='Path to output file')
       #args = parser.parse_args()
        parser.add_argument("output", nargs='*', default=argparse.SUPPRESS)
        args = parser.parse_args(namespace=argparse.Namespace(output=None))

        # Create configuration
        config = AudioRecorder.Config(args)

        # List available microphone devices
        if not config.output:
                print("==========================================================")
                devices = AudioRecorder.list(config)
                print("Available microphone devices:")
                if devices:
                        for device in devices:
                                print(f"- device ID: {device[0]}, name:{device[1]}")
                else:
                        print("No microphone devices found.")
                sys.exit(0)

        if config.verbosity > 0:
                print("==========================================================")
                print("config:")
                print(config)

        # Create recorder
        recorder = AudioRecorder(config)
        recorder.show(mirror=True)




if __name__ == '__main__':
        main()
