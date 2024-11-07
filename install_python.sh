#!/bin/bash

# Download Python installer
wget https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe

# Install Python with Wine
wine python-3.8.10.exe /quiet InstallAllUsers=1 PrependPath=1

# Wait for installation to complete
sleep 10

# Install pywin32
wine C:\\Python38\\python.exe -m pip install --no-cache-dir pywin32==228

# Clean up
rm python-3.8.10.exe