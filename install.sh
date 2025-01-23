#!/bin/bash
set -e

# Requirement check
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python first."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git first."
    exit 1
fi

git clone https://github.com/0xnoid/PostmanCollector
cd RepoRepo
rm install.sh

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


python pyfile.py -h


echo "Installation complete! RepoRepo has been set up in a virtual environment."