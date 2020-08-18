#!/usr/bin/env bash
path=$(dirname $(realpath $0))
cd $path
# assuming the existance of virtual environment .venv
source .venv/bin/activate
python3 app.py

