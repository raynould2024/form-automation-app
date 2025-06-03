#!/bin/bash
# Install Chrome and ChromeDriver for Selenium
echo "Starting Chrome installation..."
apt-get update || { echo "apt-get update failed"; exit 1; }
apt-get install -y wget unzip || { echo "apt-get install wget unzip failed"; exit 1; }
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - || { echo "Adding Chrome key failed"; exit 1; }
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt-get update || { echo "apt-get update after Chrome repo failed"; exit 1; }
apt-get install -y google-chrome-stable || { echo "Chrome installation failed"; exit 1; }
echo "Chrome installed successfully: $(google-chrome --version)"
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
echo "Detected Chrome version: $CHROME_VERSION"
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip || { echo "ChromeDriver download failed"; exit 1; }
unzip /tmp/chromedriver.zip -d /usr/local/bin/ || { echo "ChromeDriver unzip failed"; exit 1; }
chmod +x /usr/local/bin/chromedriver || { echo "chmod failed"; exit 1; }
echo "ChromeDriver installed at: $(ls -l /usr/local/bin/chromedriver)"