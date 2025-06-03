#!/bin/bash
echo "=== Starting render-build.sh execution ==="
echo "Installing Chrome and ChromeDriver manually..."

# Use /tmp as the base directory (writable)
mkdir -p /tmp/chrome-install
cd /tmp/chrome-install

# Download and extract Chrome
echo "Downloading Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O chrome.deb || {
    echo "Failed to download Chrome. Using fallback URL..."
    wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_127.0.6533.88-1_amd64.deb -O chrome.deb || {
        echo "Failed to download Chrome from fallback URL. Exiting..."
        exit 1
    }
}
echo "Extracting Chrome..."
ar x chrome.deb
# Check for data.tar.* (handle different compression formats)
if [ -f data.tar.xz ]; then
    tar -xJf data.tar.xz -C /tmp/chrome-install
elif [ -f data.tar.gz ]; then
    tar -xzf data.tar.gz -C /tmp/chrome-install
else
    echo "No valid data.tar.* file found in .deb package. Exiting..."
    exit 1
fi
mkdir -p /tmp/chrome
cp -r /tmp/chrome-install/opt/google/chrome/* /tmp/chrome/ || {
    echo "Failed to copy Chrome files. Exiting..."
    exit 1
}
echo "Chrome installed at: $(ls -l /tmp/chrome/)"

# Download and install ChromeDriver
echo "Downloading ChromeDriver..."
wget -q https://chromedriver.storage.googleapis.com/127.0.6533.88/chromedriver_linux64.zip -O chromedriver.zip || {
    echo "Failed to download ChromeDriver. Using fallback URL..."
    wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/127.0.6533.88/linux64/chromedriver-linux64.zip -O chromedriver.zip || {
        echo "Failed to download ChromeDriver from fallback URL. Exiting..."
        exit 1
    }
}
echo "Extracting ChromeDriver..."
unzip chromedriver.zip -d /tmp/chromedriver || {
    echo "Failed to unzip ChromeDriver. Exiting..."
    exit 1
}
chmod +x /tmp/chromedriver/chromedriver
# Create a symlink to a standard location (writable via symlink)
ln -sf /tmp/chromedriver/chromedriver /usr/local/bin/chromedriver || {
    echo "Failed to create symlink for ChromeDriver. Exiting..."
    exit 1
}
echo "ChromeDriver installed at: $(ls -l /usr/local/bin/chromedriver)"

echo "=== Completed render-build.sh execution ==="