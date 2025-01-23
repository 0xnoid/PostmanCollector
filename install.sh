#!/bin/bash
set -e

# Vibe check
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python first."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git first."
    exit 1
fi

git clone https://github.com/0xnoid/PostmanCollector
cd PostmanCollector
rm install.sh

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


python PostmanCollector.py -h


echo "Installation complete! Postman Collector has been set up with a Python Virtual Environment"