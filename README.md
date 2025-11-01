# Intro
Set of tools to capture media streams and pack those into container, mp4 or mkv.




# Setup 
Assume that ***python*** and ***pip3*** are installed by now. \
Or install ***python*** manually:
```
sudo apt update
 && sudo apt install -y python3
 && python3-pip
 && python3-venv
```




## 1-st create local python environment
```
python3 -m venv .venv
 && source .venv/bin/activate
```
Starting now on, assume that any py code is run for that newly created python environment, i.e. ***source .venv/bin/activate*** as called.




## 2-nd install all mandatory python packages
```
pip install opencv-python
 && pip install opencv-contrib-python 
```



# Tools

## VideoRecorder.py, VideoRecorder.sh
## AudioRecorder.py, AudioRecorder.sh
## Container.sh





# Referenses
* https://gist.github.com/tedmiston/6060034

























# pyaudio




## Option A(install the pre-compiled PyAudio package directly from Ubuntu's repositories)
```
sudo apt install python3-pyaudio
```




## Option B(???)
```
sudo apt update
sudo apt install python3-dev portaudio19-dev
pip3 install pyaudio
```




# Extra tools

## mkvtoolnix-gui
```
sudo apt install mkvtoolnix-gui
```
