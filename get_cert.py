import urllib.request
import os

url = "https://cockroachlabs.cloud/clusters/cert"
print(f"⬇️ Downloading from {url}...")

try:
    # Download
    urllib.request.urlretrieve(url, "root.crt")

    # Check integrity
    size = os.path.getsize("root.crt")
    with open("root.crt", "r") as f:
        header = f.readline().strip()

    print(f"✅ Size: {size} bytes")
    print(f"📄 Header: {header}")

    if size > 1000 and "BEGIN CERTIFICATE" in header:
        print("🚀 File is VALID.")
    else:
        print("❌ File is INVALID/CORRUPT.")

except Exception as e:
    print(f"❌ Error: {e}")