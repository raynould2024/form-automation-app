#!/bin/bash
echo "=== Starting render-build.sh execution ==="
echo "Installing Chrome and ChromeDriver manually..."

# Create a writable temp directory
mkdir -p /tmp/chrome-install
cd /tmp/chrome-install

# Download Chrome .deb package
echo "Downloading Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O chrome.deb || {
    echo "Failed to download Chrome. Using fallback URL..."
    wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_127.0.6533.88-1_amd64.deb -O chrome.deb || {
        echo "Failed to download Chrome from fallback URL. Exiting..."
        exit 1
    }
}

# Extract .deb package using ar (doesn't require filesystem writes)
echo "Extracting Chrome .deb package..."
ar x chrome.deb
tar -xzf data.tar.gz -C /tmp/chrome-install
mkdir -p /opt/chrome
cp -r /tmp/chrome-install/opt/google/chrome/* /opt/chrome/ || {
    echo "Failed to copy Chrome files. Exiting..."
    exit 1
}
echo "Chrome installed at: $(ls -l /opt/chrome/)"

# Download ChromeDriver
echo "Downloading ChromeDriver..."
wget -q https://chromedriver.storage.googleapis.com/127.0.6533.88/chromedriver_linux64.zip -O chromedriver.zip || {
    echo "Failed to download ChromeDriver. Using fallback URL..."
    wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/127.0.6533.88/linux64/chromedriver-linux64.zip -O chromedriver.zip || {
        echo "Failed to download ChromeDriver from fallback URL. Exiting..."
        exit 1
    }
}

# Extract ChromeDriver
echo "Extracting ChromeDriver..."
unzip chromedriver.zip -d /usr/local/bin/ || {
    echo "Failed to unzip ChromeDriver. Exiting..."
    exit 1
}
chmod +x /usr/local/bin/chromedriver || {
    echo "Failed to set permissions for ChromeDriver. Exiting..."
    exit 1
}
echo "ChromeDriver installed at: $(ls -l /usr/local/bin/chromedriver)"

echo "=== Completed render-build.sh execution ==="