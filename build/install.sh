#!/bin/bash

# Função para carregar modelo da impressora do JSON
load_printer_model() {
    local json_file="~/syncraft-machine.json"  # JSON na pasta raiz do sistema
    
    if [ ! -f "$json_file" ]; then
        echo "ERRO: Arquivo JSON não encontrado em $json_file"
        exit 1
    fi
    
    # Verificar se jq está instalado
    if ! command -v jq &> /dev/null; then
        echo "Instalando jq para processamento JSON..."
        apt-get update && apt-get install -y jq
    fi
    
    # Carregar modelo da impressora do JSON
    PRINTER_MODEL=$(jq -r '.printerModel // empty' "$json_file" 2>/dev/null)
    
    if [ -z "$PRINTER_MODEL" ] || [ "$PRINTER_MODEL" = "null" ]; then
        echo "ERRO: Modelo da impressora não encontrado no JSON"
        exit 1
    fi
    
    echo "Modelo carregado do JSON: $PRINTER_MODEL"
}

# Carregar configuração do JSON
echo '---------------- Carregando Configuração JSON'
load_printer_model

echo '---------------- Configuração do Modelo da Impressora'
echo "MODELO DETECTADO: $PRINTER_MODEL"
echo "MODEL=$PRINTER_MODEL" > /home/pi/syncraft-scripts/printer_model.conf

SCRIPTPATH=$(dirname -- "$(readlink -f -- "$0")")

echo '---------------- VLC Install'
apt-get install -y vlc

echo '---------------- Syncraft Scripts Install'
cat "$SCRIPTPATH"/syncraft-scripts.service > /etc/systemd/system/syncraft-scripts.service
systemctl unmask syncraft-scripts.service
systemctl daemon-reload
systemctl enable syncraft-scripts
systemctl set-default multi-user.target
systemctl restart syncraft-scripts.service

echo '---------------- Udiskie Install'
apt-get install -y udiskie
echo 'ENV{ID_FS_USAGE}=="filesystem", ENV{UDISKS_FILESYSTEM_SHARED}="1"' > /etc/udev/rules.d/99-udisks2.rules
cat "$SCRIPTPATH"/10-udisks.pkla > /etc/polkit-1/localauthority/50-local.d/10-udisks.pkla

echo '---------------- Syncraft USB Install'
cat "$SCRIPTPATH"/syncraft-usb.service > /etc/systemd/system/syncraft-usb.service
systemctl unmask syncraft-usb.service
systemctl daemon-reload
systemctl enable syncraft-usb
systemctl restart syncraft-usb.service

echo '---------------- GCODE folder permissions'
ln -s /media/ /home/pi/printer_data/gcodes/USB
chown pi /home/pi/printer_data/gcodes/USB
mkdir -p /home/pi/printer_data/gcodes/.JOB
chown pi /home/pi/printer_data/gcodes/.JOB

echo '---------------- Syncraft BacklashCompensation Install'
cat "$SCRIPTPATH"/syncraft-backlash-watcher.service > /etc/systemd/system/syncraft-backlash-watcher.service
systemctl daemon-reload
cd /home/pi/syncraft-scripts/scripts
pip3 install watchdog
systemctl enable syncraft-backlash-watcher
systemctl restart syncraft-backlash-watcher.service

echo '---------------- Instalação Concluída'
echo "Modelo da impressora: $PRINTER_MODEL"
echo "Configuração salva em: /home/pi/syncraft-scripts/printer_model.conf"