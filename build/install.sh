SCRIPTPATH=$(dirname -- "$(readlink -f -- "$0")")

cat "$SCRIPTPATH"/build/rc.local > /etc/rc.local
chmod +x /etc/rc.local

cat "$SCRIPTPATH"/build/syncraft-scripts.service > /etc/systemd/system/syncraft-scripts.service
sudo systemctl unmask syncraft-scripts.service
sudo systemctl daemon-reload
sudo systemctl enable syncraft-scripts
sudo systemctl set-default multi-user.target
sudo adduser "$USER" tty