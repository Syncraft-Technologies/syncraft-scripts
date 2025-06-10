sudo service syncraft-scripts stop
sudo rm /etc/systemd/system/syncraft-scripts.service

apt-get remove udiskie
sudo rm /etc/udev/rules.d/99-udisks2.rules
sudo rm /etc/polkit-1/localauthority/50-local.d/10-udisks.pkla
rm -rf ~/printer_data/gcodes/USB
rm -rf ~/printer_data/gcodes/.JOB
service syncraft-usb stop
rm /etc/systemd/system/syncraft-usb.service

service syncraft-backlash-watcher stop
rm /etc/systemd/system/syncraft-backlash-watcher.service