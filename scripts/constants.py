import os
import pathlib
import json
from datetime import date

def is_christmas():
	today = date.today()
	return today.month == 12 and today.day == 25

def is_new_year():
	today = date.today()
	return (today.month == 12 and today.day == 31) or (today.month == 1 and today.day == 1)

HOME_DIR = os.path.expanduser("~")
SYNCRAFT_SCRIPTS_DIR = pathlib.Path(__file__).parent.parent.resolve()
SYNCRAFT_MACHINE_PATH = os.path.join(HOME_DIR, "syncraft-machine.json")
BOOT_VIDEOS_DIR = os.path.join(SYNCRAFT_SCRIPTS_DIR, "boot_videos")
BOOT_VIDEO_PATH = os.path.join(BOOT_VIDEOS_DIR, "default.mp4")

try:
	with open(SYNCRAFT_MACHINE_PATH) as file:
		machine_json = json.load(file)
		if machine_json["bootVideo"] in os.listdir(BOOT_VIDEOS_DIR):
			BOOT_VIDEO_PATH = machine_json["bootVideo"]
except:
	pass

if is_christmas():
	BOOT_VIDEO_PATH = os.path.join(BOOT_VIDEOS_DIR, "snow.mp4")

if is_new_year():
	BOOT_VIDEO_PATH = os.path.join(BOOT_VIDEOS_DIR, "fireworks.mp4")