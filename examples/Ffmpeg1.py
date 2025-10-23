#!/usr/bin/env python

import cv2
import ffmpeg #https://kkroening.github.io/ffmpeg-python/
import time
import numpy as np

# Open the camera
cap = cv2.VideoCapture(0)  # 0 for default camera

if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

# Get camera frame properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30 # Default to 30 if not available



# FFmpeg output settings
output_filename = "output.mp4"
process = (
        ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{width}x{height}', r=fps)
        .output(output_filename, pix_fmt='yuv420p', vcodec='libx264')
        .overwrite_output()
        .run_async(pipe_stdin=True)
)

try:
        while True:
                ret, frame = cap.read()
                if not ret:
                        print("Failed to grab frame.")
                        break
                cv2.circle(frame, (100, 100), 100, (0, 255, 0), 10)

                # Write the frame to FFmpeg's stdin
                process.stdin.write(frame.astype(np.uint8).tobytes())

                # Optional: Display the frame
                cv2.imshow('Camera Feed', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

except KeyboardInterrupt:
        print("Stopping capture and video creation.")
finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        process.stdin.close()
        process.wait()
        print("Video saved as", output_filename)
