# Syncraft Scripts

Scripts e utilitários para impressoras 3D **Syncraft**.

## Índice

* [Requisitos](#requisitos)
* [Instalação](#instalação)
* [Configuração da Máquina (JSON)](#configuração-da-máquina-json)
* [Habilitar Controle de Serviços via Moonraker](#habilitar-controle-de-serviços-via-moonraker)

  * [1) Provider do Moonraker (systemd)](#1-provider-do-moonraker-systemd)
  * [2) Regras do PolicyKit](#2-regras-do-policykit)
  * [3) Lista de serviços permitidos (allowed services)](#3-lista-de-serviços-permitidos-allowed-services)
  * [4) CORS e Trusted Clients](#4-cors-e-trusted-clients)
  * [5) Testes rápidos](#5-testes-rápidos)
* [Frontend (Vite/Vue)](#frontend-vitevue)
* [Instalação dos Serviços](#instalação-dos-serviços)
* [Gerenciamento dos Serviços](#gerenciamento-dos-serviços)
* [Desinstalação](#desinstalação)
* [Solução de Problemas](#solução-de-problemas)
* [Segurança](#segurança)
* [Licença](#licença)

---

## Requisitos

* Linux (Debian/Ubuntu-like)
* Acesso de superusuário (`sudo`)
* `git` instalado
* **Moonraker** instalado e funcional
* **systemd** (DBus recomendado)

---

## Instalação

1. Vá ao diretório home:

   ```bash
   cd ~
   ```

2. Clone este repositório:

   ```bash
   git clone https://github.com/Syncraft-Technologies/syncraft-scripts.git
   ```

---

## Configuração da Máquina (JSON)

A UI e os serviços utilizam o arquivo:

```
/printer_data/config/syncraft-machine.json
```

> **Observação:** versões antigas usavam `~/syncraft-machine.json`. Padronizado agora em **`/printer_data/config`** (compatível com os endpoints `server/files/config/...` do Moonraker).

### Criar arquivo e permissões

```bash
sudo install -d -m 0755 /printer_data/config
sudo touch /printer_data/config/syncraft-machine.json
sudo chown syncraft:syncraft /printer_data/config/syncraft-machine.json
sudo chmod 0644 /printer_data/config/syncraft-machine.json
```

> Substitua `syncraft:syncraft` pelo usuário/grupo corretos do seu ambiente.

### Exemplo de configuração

```json
{
  "printerModel": "X1",
  "bc_x0": 0.0,
  "bc_x1": 0.0,
  "bc_y0": 0.0,
  "bc_y1": 0.0,
  "bootVideo": "default.mp4",
  "welcomeScreen": false
}
```

### Parâmetros

| Parâmetro       | Descrição                                                                          | Valores            |
| --------------- | ---------------------------------------------------------------------------------- | ------------------ |
| `printerModel`  | Modelo da impressora                                                               | `"X1"` ou `"IDEX"` |
| `bc_x0`,`bc_y0` | Backlash X/Y do E0 (X1: único extrusor; IDEX: extrusor principal)                  | número             |
| `bc_x1`,`bc_y1` | Backlash X/Y do E1 (somente IDEX; para X1 a UI replica os mesmos valores em E0/E1) | número             |
| `bootVideo`     | Vídeo na inicialização                                                             | arquivo            |
| `welcomeScreen` | Habilita vídeo de primeira inicialização                                           | `true/false`       |

---

## Habilitar Controle de Serviços via Moonraker

A UI aciona diretamente a API do Moonraker para **parar** e **reiniciar** serviços. Habilite:

### 1) Provider do Moonraker (systemd)

No `moonraker.conf`:

```ini
[machine]
provider: systemd_dbus     # recomendado
# provider: systemd_cli    # alternativa caso DBus não esteja disponível
```

Reinicie o Moonraker após alterar:

```bash
sudo systemctl restart moonraker
```

### 2) Regras do PolicyKit

Permitem ao Moonraker controlar serviços via DBus (executar uma única vez):

```bash
cd ~/moonraker
./scripts/set-policykit-rules.sh
```

### 3) Lista de serviços permitidos (allowed services)

Edite/crie `~/printer_data/moonraker.asvc` com **um serviço por linha**, **sem** a extensão `.service`:

```
klipper_mcu
webcamd
MoonCord
KlipperScreen
crowsnest
syncraft-usb
syncraft-backlash-watcher
```

> Se o unit no systemd for `syncraft-usb.service`, coloque **`syncraft-usb`** aqui.
> Dica: confira os nomes com:
>
> ```bash
> systemctl list-units --type=service | grep -Ei 'klipper|moon|screen|crow|syncraft'
> ```

### 4) CORS e Trusted Clients

Se a UI roda via Vite em `http://<seu-ip>:5173`, autorize no `moonraker.conf`:

```ini
[authorization]
cors_domains:
    https://my.mainsail.xyz
    http://my.mainsail.xyz
    http://*.local
    http://*.lan
    *://localhost:8080
    http://localhost:5173
    # http://<ip-da-sua-máquina>:5173

trusted_clients:
    10.0.0.0/8
    127.0.0.0/8
    169.254.0.0/16
    172.16.0.0/12
    192.168.0.0/16
    FE80::/10
    ::1/128
```

Reinicie o Moonraker:

```bash
sudo systemctl restart moonraker
```

### 5) Testes rápidos

* **Ver serviços disponíveis**:

  ```bash
  curl http://<IP-DA-IMPRESSORA>:7125/machine/system_info
  ```

  Procure `available_services` e confirme `syncraft-backlash-watcher`.

* **Parar / Reiniciar (via Moonraker)**:

  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"service":"syncraft-backlash-watcher"}' \
    http://<IP-DA-IMPRESSORA>:7125/machine/services/stop

  curl -X POST -H "Content-Type: application/json" \
    -d '{"service":"syncraft-backlash-watcher"}' \
    http://<IP-DA-IMPRESSORA>:7125/machine/services/restart
  ```

---

## Frontend (Vite/Vue)

A página **SyncraftCalibration.vue** lê/escreve o JSON via Moonraker (`/server/files/...`) e aciona serviços via:

* `POST /machine/services/stop`
* `POST /machine/services/restart`

### Variáveis `.env` (frontend)

Crie/ajuste `./.env` na raiz do projeto Vite:

```env
# (opcional) URL do Moonraker; se ausente, a UI tenta base relativa via proxy
VITE_MOONRAKER_URL=http://<IP-DA-IMPRESSORA>:7125

# Nome do serviço SEM ".service"
VITE_SERVICE_NAME=syncraft-backlash-watcher
```

### Comandos UI

```bash
# desenvolvimento
npm run dev
# build
npm run build
# preview
npm run preview
```

---

## Instalação dos Serviços

> **Importante:** Garanta o JSON em `/printer_data/config/syncraft-machine.json`.

Execute o instalador:

```bash
sudo ./syncraft-scripts/build/install.sh
```

---

## Gerenciamento dos Serviços

### Pela interface (recomendado)

* **Parar serviço e zerar parâmetros** (para + zera + salva).
* **Salvar parâmetros e reiniciar serviço**.

### Via terminal (alternativa)

```bash
# reiniciar
sudo systemctl restart syncraft-backlash-watcher.service

# parar
sudo systemctl stop syncraft-backlash-watcher.service

# iniciar
sudo systemctl start syncraft-backlash-watcher.service

# status
sudo systemctl status syncraft-backlash-watcher.service

# logs ao vivo
sudo journalctl -u syncraft-backlash-watcher.service -f
```

---

## Desinstalação

```bash
sudo ./syncraft-scripts/build/uninstall.sh
```

---

## Solução de Problemas

**UI retorna erro ao parar/reiniciar:**

* Verifique o **provider** no `moonraker.conf` (`systemd_dbus` recomendado).
* Execute `./scripts/set-policykit-rules.sh` (DBus).
* Confira `~/printer_data/moonraker.asvc` (um nome por linha, sem `.service`).
* Ajuste `cors_domains`/`trusted_clients` para a origem da UI (ex.: `:5173`).
* Logs:

  ```bash
  sudo journalctl -u moonraker -f
  sudo journalctl -u syncraft-backlash-watcher.service -f
  ```

**Alterações do JSON não surtem efeito:**

* Confirme que a UI salva em `/printer_data/config/syncraft-machine.json`.
* Após salvar, use **“Salvar parâmetros e reiniciar serviço”**.

**Arquivo JSON inválido ou ausente:**

* Valide a sintaxe (ex.: `jq`).
* Recrie e defina permissões: `0644` e dono `syncraft:syncraft` (ou equivalente).

**Serviço não listado no Moonraker:**

* `systemctl list-units --type=service | grep syncraft`
* Ajuste o nome em `moonraker.asvc` (sem `.service`) e reinicie o Moonraker.

---

## Segurança

* **Allowed services:** liste apenas o que precisa ser controlado.
* Restrinja `cors_domains` à origem real da sua UI.
* Evite expor Moonraker na internet sem VPN/túnel/firewall.
* Prefira `systemd_dbus` + PolicyKit.

---

## Licença

Este projeto é mantido pela Syncraft Technologies. Consulte `LICENSE` para detalhes.
