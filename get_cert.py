import urllib.request
import os

# This is the universal CA for all CockroachDB Serverless clusters
url = "https://cockroachlabs.cloud/clusters/cert"
filename = "root.crt"

print(f"⬇️ Downloading cert from {url}...")

try:
    urllib.request.urlretrieve(url, filename)
    size = os.path.getsize(filename)
    print(f"✅ Download Complete! File: {filename}")
    print(f"📏 Size: {size} bytes")
    
    if size < 100:
        print("❌ WARNING: File is too small. It might be corrupt.")
    else:
        print("🚀 Valid certificate acquired.")
except Exception as e:
    print(f"❌ Error: {e}")