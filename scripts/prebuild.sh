#!/bin/bash

# Update package lists
sudo apt-get update

# Install required packages
sudo apt-get install -y build-essential cmake
sudo apt-get install -y libopenblas-dev liblapack-dev
sudo apt-get install -y libx11-dev libgtk-3-dev
sudo apt-get install -y libgl1-mesa-glx
sudo apt-get install -y libglib2.0-dev