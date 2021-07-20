#!/bin/bash

# Configuration parameters
export GAME_ROOT=$HOME/Games/guild-wars-2
export WINE_RUNNER=$HOME/.local/share/lutris/runners/wine/lutris-6.10-7-x86_64/bin/wine

# Set up environment variables for wine
export WINEPREFIX=$GAME_ROOT
export WINEESYNC=1
export DXVK_STATE_CACHE_PATH=$GAME_ROOT
export __GL_SHADER_DISK_CACHE_PATH=$GAME_ROOT
export SDL_VIDEO_FULLSCREEN_DISPLAY=off
export WINEARCH=win64
export WINE_LARGE_ADDRESS_AWARE=1
export WINEDLLOVERRIDES='api-ms-win-crt-private-l1-1-0,ucrtbase=n,b;d3d10,d3d10_1,d3d10core,d3d11,dxgi=n;d3d12,nvapi,nvapi64='

# Run the python script in wine
"$WINE_RUNNER" "$WINEPREFIX/drive_c/Program Files/Python/pythonw.exe" "$WINEPREFIX/drive_c/Program Files/Flan/wine_mumble_link_converter.py"
