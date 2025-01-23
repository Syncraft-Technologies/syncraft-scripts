# Syncraft scripts

This repository contains scripts for Syncraft 3D printers.

## Building a machine

1. Clone the repository at home (`~`):
	```bash
	cd ~
	git clone https://github.com/Syncraft-Technologies/syncraft-scripts.git
	```
2. Run `apply.sh`
	```bash
	./build/apply.sh
	```

## Machine configuration

You can create a file called `syncraft-machine.json` at home (`~`) in order to specify desired configurations.

### Allowed values

#### `bootVideo`

Will be the video played on boot. Must be a string with any of the file names (with extension) from the `boot_videos` directory.