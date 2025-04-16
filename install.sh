#!/bin/bash

echo "Installing Ouranos Chatbot"
ORIGIN=$PWD

cd $OURANOS_DIR

# Activate Ouranos venv
source venv/bin/activate

# Get the Chatbot and install the package
cd "lib"

git clone https://github.com/vaamb/ouranos-chatbot.git "ouranos-chatbot"; cd "ouranos-chatbot"
pip install -e .

cd "$ORIGIN"
echo "Ouranos Chatbot installed"

exit
