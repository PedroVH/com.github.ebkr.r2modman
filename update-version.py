#!/usr/bin/env python3
"""
- Checks Github API for newest version of r2modman
- Downloads it for checksum calculation 
- Updates Flatpak manifest accordingly
"""
# %%

# Imports
# Only modules in the standard library were chosen to avoid needing to install Python dependencies
import hashlib
import re
import json
import urllib.request

# Pre-defined values
REPO_API_RELEASE_URL = "https://api.github.com/repos/ebkr/r2modmanPlus/releases/latest"
FLATPACK_MANIFEST_NAME = "com.github.ebkr.r2modman.yaml"
FLATPACK_APPDATA_NAME = "com.github.ebkr.r2modman.appdata.xml"


# Get JSON object containing info about all releases
api_response = urllib.request.urlopen(REPO_API_RELEASE_URL).read()
response_json = json.loads(api_response)

# Get content of newest release
release_version = response_json["tag_name"].replace("v", "")
release_date = response_json["published_at"].split("T")[0]
release_body = response_json["body"]
release_changes = release_body.split("##")[1]
print(f"Newest version is {release_version} published in {release_date}")

# The part of the JSON object that refers to the tar archive
tar_object = [x for x in json.loads(
    api_response)["assets"] if "tar.gz" in x["name"]][0]


# Simple check to ensure that versions match up
assert(release_version in tar_object["name"])

# Download tar archive file for checksum calculation
g = urllib.request.urlopen(tar_object["browser_download_url"])
with open(tar_object["name"], "bw") as f:
    f.write(g.read())

# Calculate SHA256 checksum to update in manifest
sha256_hash = hashlib.sha256()
with open(tar_object["name"], "rb") as f:
    # Read and update hash string value in blocks of 4K
    for byte_block in iter(lambda: f.read(4096), b""):
        sha256_hash.update(byte_block)
    release_checksum = sha256_hash.hexdigest()


# Read Flatpak manifest
with open(FLATPACK_MANIFEST_NAME, "rt") as f:
    file_content = f.read()

# Set version number, size, and checksum
file_content = re.sub(r"(\d+\.\d+\.\d+)", release_version, file_content)
file_content = re.sub(r"size: \d+", f"size: {tar_object['size']}", file_content, 0, re.MULTILINE)
file_content = re.sub(r"sha256: [0-9a-fA-F]+", f"sha256: {release_checksum}", file_content, 0, re.MULTILINE)

# Write back updated content
with open(FLATPACK_MANIFEST_NAME, "wt") as f:
    f.write(file_content)


# Read appdata.xml
with open(FLATPACK_APPDATA_NAME, "rt") as f:
    file_content = f.read()

file_content = file_content.split("<release version=")[0] + "%RELEASE%" + file_content.split("</release>")[1]

new_release = (f"<release version=\"{release_version}\" date=\"{release_date}\">\n"
               f"\t\t\t<description>")
for change in release_changes.split("\r\n* "):
    change = change.replace("\r", "").replace("\n", "")
    new_release = f"{new_release}\n\t\t\t\t<p>{change}</p>"
new_release = f"{new_release} \n\t\t\t</description>\n\t\t</release>"

file_content = file_content.replace("%RELEASE%", new_release)

# Write back updated content
with open(FLATPACK_APPDATA_NAME, "wt") as f:
    f.write(file_content)

print("Done")
