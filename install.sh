#!/bin/bash

# Get directory of this bash script
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

# Load Configuration parameters
. "$DIR/configuration.sh"

# Create venv
if [[ -d "$HOME/Venv/flan" ]]; then
    echo "A venv already exists for flan"
else
    echo "Creating a venv"
    mkdir -p "$HOME/Venv/flan"
    python3.9 -m venv "$HOME/Venv/flan"
    if [[ $? != 0 ]]; then
        rm -rf "$HOME/Venv/flan"
        exit 1
    fi
    # Install python deps
    . "$HOME/Venv/flan/bin/activate"
    pip install PyQt5
fi

# Copy python converter into wine prefix
echo "Copying converter.py into wine prefix"
mkdir -p "$GAME_ROOT/drive_c/Program Files/Flan"
cp "$DIR/src/converter.py" "$GAME_ROOT/drive_c/Program Files/Flan/converter.py"

# Install 