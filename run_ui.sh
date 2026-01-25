#!/bin/bash
set -e
export DISPLAY=:0

# Xauthority は環境によって必要（あっても害なし）
if [ -f "$HOME/.Xauthority" ]; then
  export XAUTHORITY="$HOME/.Xauthority"
fi

cd "$HOME/car_dash"
python3 ui_main.py
