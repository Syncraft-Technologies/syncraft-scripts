# Syncraft scripts

This repository contains scripts for Syncraft 3D printers.

## Building a machine

1. Clone the repository at home (`~`):
	```bash
	cd ~
	```
	```bash
	git clone https://github.com/Syncraft-Technologies/syncraft-scripts.git
	```
2. Run `install.sh` as superuser

	2.1. Install Syncraft X1
	
	```bash
	sudo ./syncraft-scripts/build/install.sh X1
	```

	2.2. Install Syncraft IDEX
	
	```bash
	sudo ./syncraft-scripts/build/install.sh IDEX
	```

## Machine configuration

You can create a file called `syncraft-machine.json` at home (`~`) in order to specify desired configurations.

### Allowed values

#### `Backlash Compensation`

1. X1

	Set in the file `scripts/offsets.ini` the compensation in X and Y axis.
	```bash
	X: 0.0
	Y: 0.0
	```

2. IDEX
	
	Set in the file `scripts/offsets_T0.ini` the compensation in X and Y axis.
	```bash
	X: 0.0
	Y: 0.0
	```

	Set in the file `scripts/offsets_T1.ini` the compensation in X and Y axis.
	```bash
	X: 0.0
	Y: 0.0 // The same from T0
	```

Once changed offsets files, it´s necessary restart the service:
 ```bash
sudo systemctl restart syncraft-backlash-watcher.service
```

If needed, check the status of the service with the following command:
 ```bash
sudo systemctl status syncraft-backlash-watcher.service
```

#### `bootVideo`

Will be the video played on boot. Must be a string with any of the file names (with extension) from the `boot_videos` directory.

#### `welcomeScreen`

Set this to `true` if you want the `first_boot.mp4` video to play once on the next startup.

## Remove all services

1. Run `uninstall.sh` as superuser
	```bash
	sudo ./syncraft-scripts/build/uninstall.sh
	```
