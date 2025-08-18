# Syncraft Scripts

Este repositório contém scripts para impressoras 3D Syncraft.

## Índice

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração da Máquina](#configuração-da-máquina)
- [Instalação dos Serviços](#instalação-dos-serviços)
- [Gerenciamento dos Serviços](#gerenciamento-dos-serviços)
- [Desinstalação](#desinstalação)
- [Solução de Problemas](#solução-de-problemas)

## Requisitos

- Sistema operacional Linux
- Acesso de superusuário (sudo)
- Git instalado

## Instalação

1. Navegue até o diretório home:
   ```bash
   cd ~
   ```

2. Clone o repositório:
   ```bash
   git clone https://github.com/Syncraft-Technologies/syncraft-scripts.git
   ```

## Configuração da Máquina

Antes de instalar os serviços, você deve criar um arquivo de configuração chamado `syncraft-machine.json` no diretório home (`~`).

### Exemplo de configuração:

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

### Parâmetros de configuração:

| Parâmetro | Descrição | Valores Aceitos |
|-----------|-----------|-----------------|
| `printerModel` | Modelo da impressora | `"X1"` ou `"IDEX"` |
| `bc_x0` | Compensação de backlash no eixo X para extrusora 0 (X1) ou extrusora principal (IDEX) | Número decimal |
| `bc_y0` | Compensação de backlash no eixo Y para extrusora 0 (X1) ou extrusora principal (IDEX) | Número decimal |
| `bc_x1` | Compensação de backlash no eixo X para extrusora 1 (apenas modelo IDEX) | Número decimal |
| `bc_y1` | Compensação de backlash no eixo Y para extrusora 1 (apenas modelo IDEX) | Número decimal |
| `bootVideo` | Vídeo reproduzido durante a inicialização | Nome do arquivo (com extensão) do diretório `boot_videos` |
| `welcomeScreen` | Ativa a reprodução do vídeo de primeira inicialização | `true` ou `false` |

## Instalação dos Serviços

⚠️ **Importante**: Certifique-se de que o arquivo `syncraft-machine.json` esteja configurado antes de prosseguir.

Execute o script de instalação como superusuário:

```bash
sudo ./syncraft-scripts/build/install.sh
```

## Gerenciamento dos Serviços

### Reiniciar o serviço após alterações nos parâmetros

Quando você alterar os valores de compensação de backlash, é necessário reiniciar o serviço:

```bash
sudo systemctl restart syncraft-backlash-watcher.service
```

### Verificar o status do serviço

Para verificar se o serviço está funcionando corretamente:

```bash
sudo systemctl status syncraft-backlash-watcher.service
```

### Outros comandos úteis

- **Parar o serviço:**
  ```bash
  sudo systemctl stop syncraft-backlash-watcher.service
  ```

- **Iniciar o serviço:**
  ```bash
  sudo systemctl start syncraft-backlash-watcher.service
  ```

- **Verificar logs do serviço:**
  ```bash
  sudo journalctl -u syncraft-backlash-watcher.service -f
  ```

## Desinstalação

Para remover todos os serviços instalados:

```bash
sudo ./syncraft-scripts/build/uninstall.sh
```

## Solução de Problemas

### O serviço não inicia

1. Verifique se o arquivo `syncraft-machine.json` existe e está no formato correto
2. Verifique os logs do serviço para identificar erros específicos
3. Certifique-se de que todos os arquivos de vídeo referenciados existem no diretório apropriado

### Alterações na configuração não surtem efeito

1. Certifique-se de reiniciar o serviço após fazer alterações no arquivo de configuração
2. Verifique se o arquivo JSON possui sintaxe válida

### Arquivo de configuração não encontrado

O arquivo `syncraft-machine.json` deve estar localizado no diretório home do usuário (`~/syncraft-machine.json`).

---

## Contribuição

Para relatar problemas ou sugerir melhorias, abra uma issue no [repositório oficial](https://github.com/Syncraft-Technologies/syncraft-scripts).

## Licença

Este projeto é mantido pela Syncraft Technologies. Consulte o arquivo LICENSE para mais informações.