#!/usr/bin/env python3
"""Download video from Mega"""
from mega import Mega
import sys

mega = Mega()
m = mega.login()

print("Downloading from Mega...")
file = m.download_url("https://mega.nz/file/4RIU2DyB#otuNNuMFLghD0G1lxD2zJnXRP-2voOhcasEOnwOrn18", dest_path="test_videos")
print(f"Downloaded: {file}")
