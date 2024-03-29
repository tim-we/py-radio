#!/usr/bin/env bash
path=$(dirname "$(realpath "$0")")
exitcode=0
cd "$path" || exit
# assuming the existence of virtual environment .venv
source .venv/bin/activate

while [ "$exitcode" == 0 ]
do
  python3 app.py
  exitcode="$?"
  if [ "$exitcode" == 69 ]
  then
    git pull
    pip install -r requirements.txt
    npm --prefix ./web ci
    npm --prefix ./web run build:production
    exitcode=0
  fi
  sleep 1
done
