#!/bin/bash

echo "Installing Ouranos Chatbot"
ORIGIN=$PWD

cd $OURANOS_DIR

# Activate Ouranos venv
source venv/bin/activate

# Get the Chatbot and install the package
cd "bin"

mkdir "chatbot"; cd "chatbot"
git clone --branch stable https://gitlab.com/gaia/ouranos-chatbot.git "ouranos-chatbot"; cd "ouranos-chatbot"
pip install -r requirements.txt
pip install -e .

cd "$ORIGIN"
echo "Ouranos Chatbot installed"

exit