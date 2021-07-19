#!/bin/bash
if [[ -d "$HOME/Venv/flan" ]]; then
    echo "A venv already exists for this project."
else
    mkdir -p "$HOME/Venv/flan"
    python3.9 -m venv "$HOME/Venv/flan"
fi

echo "Use '. ~/Venv/flan/bin/activate' to activate this venv"
