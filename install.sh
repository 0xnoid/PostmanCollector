#!/bin/bash
set -e

# Vibecheck gang gang
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
echo "Installing Python requirements..."
pip install -r requirements.txt -q

python PostmanCollector.py -h

echo "Installation complete! Postman Collector has been set up with a Python Virtual Environment"
echo "Note that PostmanCollector uses Python Virtual Environment."