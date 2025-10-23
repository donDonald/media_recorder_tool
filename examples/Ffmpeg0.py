#!/usr/bin/env python

import ffmpeg #https://kkroening.github.io/ffmpeg-python/
import time

# Define input source (replace with your camera's name or index if needed)
# For Windows, 'video=Integrated Camera:audio=Microphone Array (Realtek(R) Audio)' is common
# For Linux, '/dev/video0' is common for the first webcam
# For macOS, '0' or a specific device name might be needed with 'avfoundation'
#input_source = 'video=Integrated Camera:audio=Microphone Array (Realtek(R) Audio)' 
input_source = 'video=/dev/video0'

# Define output file name
output_file = 'output.mp4'

# Create the FFmpeg process
process = (
        ffmpeg
        .input(input_source, format='v4l2') # Use 'dshow' for Windows, 'v4l2' for Linux, 'avfoundation' for macOS
        .output(output_file, pix_fmt='yuv420p') # Specify pixel format for compatibility
        .overwrite_output() # Overwrite if output file already exists
        .run_async(pipe_stdin=True, pipe_stderr=True, quiet=True) # Run asynchronously
)

# Simulate recording for a certain duration (e.g., 10 seconds)
print('Start waiting...')
time.sleep(10) 

# Send 'q' to stdin to gracefully stop the recording
print('Stop recording')
process.stdin.write('q'.encode())
process.communicate() # Wait for the process to finish
process.wait()

print('Recording finished')
