import os
import subprocess
import pathlib

def play_video(path: str):
	return subprocess.run(["sudo", "-u", "pi", "cvlc", "-f", "--no-video-title-show", path])

def play_boot_video():
	syncraft_scripts = pathlib.Path(__file__).parent.parent.resolve()
	play_video(os.path.join(syncraft_scripts, "boot_videos", "default.mp4"))