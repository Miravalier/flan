#!/bin/bash
if [[ -d "$HOME/Venv/flan" ]]; then
    echo "A venv already exists for this project."
else
    mkdir -p "$HOME/Venv/flan"
    python3.9 -m venv "$HOME/Venv/flan"
    if [[ $? != 0 ]]; then
        rm -rf "$HOME/Venv/flan"
        exit 1
    fi
    . "$HOME/Venv/flan/bin/activate"
    pip install PyQt5
fi

echo "Use '. ~/Venv/flan/bin/activate' to activate this venv"
