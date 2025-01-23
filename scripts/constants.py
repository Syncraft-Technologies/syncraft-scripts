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

play_welcome_screen = False

try:
	with open(SYNCRAFT_MACHINE_PATH) as file:
		machine_json = json.load(file)

		boot_video = machine_json.get("bootVideo")
		welcome_screen = machine_json.get("welcomeScreen")

		if boot_video in os.listdir(BOOT_VIDEOS_DIR):
			BOOT_VIDEO_PATH = os.path.join(BOOT_VIDEOS_DIR, boot_video)

		if welcome_screen == True:
			play_welcome_screen = True
			machine_json["welcomeScreen"] = False

		with open(SYNCRAFT_MACHINE_PATH, "w") as file:
			json.dump(machine_json, file, indent=2)
except:
	pass

if is_christmas():
	BOOT_VIDEO_PATH = os.path.join(BOOT_VIDEOS_DIR, "snow.mp4")

if is_new_year():
	BOOT_VIDEO_PATH = os.path.join(BOOT_VIDEOS_DIR, "fireworks.mp4")

if play_welcome_screen:
	BOOT_VIDEO_PATH = os.path.join(BOOT_VIDEOS_DIR, "first_boot.mp4")