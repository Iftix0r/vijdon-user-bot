#!/bin/bash
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your credentials!"
    exit 1
fi

python3 src/main.py
