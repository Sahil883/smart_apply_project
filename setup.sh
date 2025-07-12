#!/usr/bin/env bash

# Update packages and install dependencies
apt-get update && apt-get install -y wget apt-transport-https curl gnupg

# Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

# Install Chromium Chromedriver
apt install -y chromium-chromedriver

# Symlink to make chromedriver available in PATH
ln -s /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
