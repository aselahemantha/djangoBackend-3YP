#!/bin/bash

# Update package lists
apt-get update

# Install required packages
apt-get install -y build-essential cmake
apt-get install -y libopenblas-dev liblapack-dev
apt-get install -y libx11-dev libgtk-3-dev
apt-get install -y libgl1-mesa-glx
apt-get install -y libglib2.0-dev