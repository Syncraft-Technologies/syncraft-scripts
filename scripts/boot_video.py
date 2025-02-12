import subprocess
from constants import *

def get_os_codename():
	try:
		with open("/etc/os-release") as f:
			for line in f:
				if line.startswith("VERSION_CODENAME="):
					return line.strip().split("=")[1]
	except FileNotFoundError:
			return None

def play_video(path: str):
	os_codename = get_os_codename()

	if os_codename == "buster":
		subprocess.run(["omxplayer", path])
	elif os_codename == "bullseye":
		subprocess.run(["cvlc", "-f", "--no-video-title-show", path])

def play_boot_video():
	play_video(BOOT_VIDEO_PATH)