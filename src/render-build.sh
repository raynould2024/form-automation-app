#!/bin/bash
echo "=== Starting render-build.sh execution ==="
# Use pre-downloaded Chrome and ChromeDriver since apt-get update fails in read-only FS
echo "Installing Chrome and ChromeDriver manually..."
mkdir -p /tmp/chrome && cd /tmp/chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb /opt/chrome
echo "Chrome installed at: /opt/chrome/usr/bin/google-chrome"
wget -q https://chromedriver.storage.googleapis.com/127.0.0.0/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
echo "ChromeDriver installed at: $(ls -l /usr/local/bin/chromedriver)"
echo "=== Completed render-build.sh execution ==="