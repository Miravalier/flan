#!/bin/bash

# Fix home directory if sudo-ing
if [[ -n "$SUDO_USER" ]]; then
    export HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
fi

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

# Install embedded Python
if [[ -d "$GAME_ROOT/drive_c/Program Files/Python" ]]; then
    echo "Python is already installed in the wine prefix"
else
    echo "Installing embedded Python into wine prefix"
    curl $PYTHON_URL -o /tmp/python-embed.zip
    unzip -q /tmp/python-embed.zip -d "$GAME_ROOT/drive_c/Program Files/Python"
    rm -f /tmp/python-embed.zip
fi

# Copy python converter into wine prefix
echo "Copying converter.py into wine prefix"
mkdir -p "$GAME_ROOT/drive_c/Program Files/Flan"
cp "$DIR/src/converter.py" "$GAME_ROOT/drive_c/Program Files/Flan/converter.py"

# Make a link to run.sh in /usr/bin
echo "Creating /usr/bin/gw2_flan"
echo -e "#/bin/bash\n$DIR/run.sh" | sudo tee /usr/bin/gw2_flan >/dev/null
sudo chmod +x /usr/bin/gw2_flan