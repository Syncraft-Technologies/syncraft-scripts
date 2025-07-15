#!/usr/bin/env python3
import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

GCODE_DIR = "/home/pi/printer_data/gcodes"
MODEL_CONF = "/home/pi/syncraft-scripts/printer_model.conf"

def get_model():
    try:
        with open(MODEL_CONF, "r") as f:
            for line in f:
                if line.strip().startswith("MODEL="):
                    return line.strip().split("=")[1].upper()
    except:
        pass
    return "X1"  # fallback padrão

def get_script_path():
    model = get_model()
    if model == "IDEX":
        return "/home/pi/syncraft-scripts/scripts/backlash_compensation_idex.py"
    else:
        return "/home/pi/syncraft-scripts/scripts/backlash_compensation_x1.py"

MAX_FILE_SIZE_MB = 30

class GcodeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path

        # 1) Só lidar com .gcode
        if not filepath.endswith(".gcode"):
            return

        # 2) Ignorar arquivos temporários (.tmp, .part, .uploading)
        if any(suffix in filepath for suffix in [".tmp", ".part", ".uploading"]):
            return

        # 3) Se já existe <arquivo>.gcode.original, ignora (já processado)
        if os.path.exists(filepath + ".original"):
            return

        # 4) Ignorar arquivos muito grandes
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            print(f"[Watcher] Arquivo ignorado (muito grande: {size_mb:.2f}MB): {filepath}")
            return

        # 5) Aguarda arquivo “estabilizar” após upload
        prev_size = -1
        stable_checks = 0
        while stable_checks < 3:
            current_size = os.path.getsize(filepath)
            if current_size == prev_size:
                stable_checks += 1
            else:
                stable_checks = 0
                prev_size = current_size
            time.sleep(0.5)

        # 6) Chamamos o compensador apenas uma vez
        print(f"[Watcher] Processando arquivo: {filepath}")
        script_path = get_script_path()
        print(f"[Watcher] Modelo: {get_model()} – Usando script: {os.path.basename(script_path)}")
        subprocess.run(["python3", script_path, filepath, filepath], check=False)
        print(f"[Watcher] Pós-processamento concluído: {filepath}")

	    # 7) Agora vamos forçar o DELETE + UPLOAD para disparar o “files changed”
        base_name       = os.path.basename(filepath)          # ex: "meuarquivo.gcode"
        backup_name     = base_name + ".original"             # ex: "meuarquivo.gcode.original"
        local_path      = os.path.join(GCODE_DIR, base_name)  # ex: "/.../meuarquivo.gcode"
        backup_path     = os.path.join(GCODE_DIR, backup_name)

        try:
            # 7.1) DELETE do .original via API (isso envia um “files changed”)
            resp_delete = subprocess.run([
                "curl", "-s", "-X", "POST",
                "http://localhost:7125/server/files/delete?root=gcodes&filename=" + backup_name
            ], capture_output=True, text=True)
            if resp_delete.returncode != 0:
                raise RuntimeError(f"Erro no DELETE: {resp_delete.stderr.strip()}")
            print(f"[Watcher] DELETE bem-sucedido de: {backup_name}")

            # Breve pausa para garantir que o Moonraker processe o DELETE
            time.sleep(0.3)

            # 7.2) UPLOAD do arquivo compensado (já existe fisicamente em disk, mas o
            #       endpoint de upload irá sobrescrever e disparar novo “files changed”)
            resp_upload = subprocess.run([
                "curl", "-s", "-X", "POST",
                "http://localhost:7125/server/files/upload?root=gcodes",
                "-H", "Content-Type: multipart/form-data",
                "-F", f"file=@{local_path};filename={base_name}"
            ], capture_output=True, text=True)
            if resp_upload.returncode != 0:
                raise RuntimeError(f"Erro no UPLOAD: {resp_upload.stderr.strip()}")
            print(f"[Watcher] UPLOAD bem-sucedido de: {base_name}")

        except Exception as e:
            print(f"[Watcher] Aviso: falha no DELETE+UPLOAD para forçar refresh → {e}")
        finally:
            # 8) Marcar como processado para não repetir se houver ghost events
            open(filepath + ".processed", "a").close()

if __name__ == "__main__":
    print("[Watcher] Monitorando G-codes com segurança...")
    event_handler = GcodeHandler()
    observer = Observer()
    observer.schedule(event_handler, GCODE_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
