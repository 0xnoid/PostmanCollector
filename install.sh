#!/bin/bash
set -e

# Vibecheck
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
clear


python PostmanCollector.py -h


echo "PostmanCollector has been set up."
echo "Note that PostmanCollector uses Python Virtual Environment."