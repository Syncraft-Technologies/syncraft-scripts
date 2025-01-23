import subprocess
from constants import *

def play_video(path: str):
	return subprocess.run(["cvlc", "-f", "--no-video-title-show", path])

def play_boot_video():
	play_video(BOOT_VIDEO_PATH)