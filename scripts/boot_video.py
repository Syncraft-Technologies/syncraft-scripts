import os
import subprocess

def play_video(path: str):
	return subprocess.run(["sudo", "-u", "pi", "cvlc", "-f", "--no-video-title-show", path])

def play_boot_video():
	play_video(os.path.join(os.path.expanduser("~"), "syncraft-scripts", "boot_videos", "default.mp4"))