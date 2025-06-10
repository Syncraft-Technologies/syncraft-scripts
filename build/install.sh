SCRIPTPATH=$(dirname -- "$(readlink -f -- "$0")")

apt-get install vlc

cat "$SCRIPTPATH"/syncraft-scripts.service > /etc/systemd/system/syncraft-scripts.service
systemctl unmask syncraft-scripts.service
systemctl daemon-reload
systemctl enable syncraft-scripts
systemctl set-default multi-user.target
systemctl restart syncraft-scripts.service

apt-get install udiskie
echo 'ENV{ID_FS_USAGE}=="filesystem", ENV{UDISKS_FILESYSTEM_SHARED}="1"' > /etc/udev/rules.d/99-udisks2.rules
cat "$SCRIPTPATH"/10-udisks.pkla > /etc/polkit-1/localauthority/50-local.d/10-udisks.pkla

cat "$SCRIPTPATH"/syncraft-usb.service > /etc/systemd/system/syncraft-usb.service
systemctl unmask syncraft-usb.service
systemctl daemon-reload
systemctl enable syncraft-usb
systemctl restart syncraft-usb.service

ln -s /media/ /home/pi/printer_data/gcodes/USB
chown pi /home/pi/printer_data/gcodes/USB
mkdir /home/pi/printer_data/gcodes/.JOB
chown pi /home/pi/printer_data/gcodes/.JOB

cat "$SCRIPTPATH"/syncraft-backlash-watcher.service > /etc/systemd/system/syncraft-backlash-watcher.service
systemctl unmask syncraft-backlash-watcher.service
systemctl daemon-reload
systemctl enable syncraft-backlash-watcher
systemctl restart syncraft-backlash-watcher.service
