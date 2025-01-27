SCRIPTPATH=$(dirname -- "$(readlink -f -- "$0")")

cat "$SCRIPTPATH"/syncraft-scripts.service > /etc/systemd/system/syncraft-scripts.service
systemctl unmask syncraft-scripts.service
systemctl daemon-reload
systemctl enable syncraft-scripts
systemctl set-default multi-user.target

systemctl restart syncraft-scripts.service