# py-radio

![static analysis](https://github.com/tim-we/py-radio/workflows/static%20analysis/badge.svg)

## Install

We recommend [using a virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) for this.
Name it `.venv` as that is already on `.gitignore`.

`pip3 install -r requirements.txt`

Install [FFmpeg](https://en.wikipedia.org/wiki/FFmpeg) and PortAudio:
`sudo apt install ffmpeg libportaudio2`

Currently setting up a test library is required. Create a new folder `test_library` in this folder with the following directory structure:

    test_library/
        music/
            ...
        hosts/
            ...
        night/
            ...
        ...

## Run

`python3 app.py`
