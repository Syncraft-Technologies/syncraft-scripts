#!/usr/bin/env python3
import os
import sys

version_code = "o3HighMini0"
directoryPath = os.path.dirname(os.path.realpath(__file__))

def get_offsets():
    """
    Lê offsets de offsets.ini, ignorando comentários (“#”):
    - Se tiver 2 valores: assume X único (T0=T1) e Y.
    - Se tiver ≥3 valores: assume X_T0, X_T1 e Y.
    Retorna (offset_x_T0, offset_x_T1, offset_y).
    """
    fallback = (0.15, 0.15, 0.45)
    path = os.path.join(directoryPath, "offsets.ini")
    try:
        with open(path, "r") as f:
            # filtra linhas não vazias e sem comentários
            lines = [l.split("#",1)[0].strip() for l in f.readlines()]
            vals = [float(l) for l in lines if l]
        if len(vals) == 2:
            # X único para ambas as ferramentas
            return vals[0], vals[0], vals[1]
        if len(vals) >= 3:
            return vals[0], vals[1], vals[2]
    except Exception:
        pass
    return fallback

def parse_gcode_line(line):
    return line.rstrip("\n").split()

def reconstruct_gcode_line(tokens):
    return " ".join(tokens) + "\n"

def process_line(tokens, current_x, current_y, blX, blY,
                 offset_x_T0, offset_x_T1, offset_y,
                 current_tool, mode):
    """
    Aplica compensação de backlash em X e Y:
    - raw_offset_x dependendo de T0 ou T1
    - inverte raw_offset_x se mode=='mirror' e current_tool=='T1'
    """
    # escolhe raw X conforme ferramenta
    raw_x = offset_x_T0 if current_tool == "T0" else offset_x_T1
    # inverte em mirror/T1
    sign_x = -1 if (mode == "mirror" and current_tool == "T1") else 1
    eff_offset_x = raw_x * sign_x

    # só processa G0/G1
    if not tokens or not tokens[0].startswith(("G0","G1")):
        return tokens, current_x, current_y, blX, blY, None, False

    # extrai parâmetros
    params = {}
    token_map = {}
    has_extrusion = False
    for i,t in enumerate(tokens):
        if t[0] in ("X","Y","Z","E","F"):
            try:
                v = float(t[1:])
                params[t[0]] = v
                token_map[t[0]] = i
                if t[0] == "E":
                    has_extrusion = True
            except ValueError:
                pass

    if "X" not in params and "Y" not in params:
        return tokens, current_x, current_y, blX, blY, None, has_extrusion

    # detecta mudança de direção
    x_changed = False
    y_changed = False

    # --- X ---
    new_x = current_x
    new_blX = blX
    if "X" in params:
        x_val = params["X"]
        if blX:
            if (x_val + eff_offset_x) >= current_x:
                new_x, new_blX = x_val + eff_offset_x, True
            else:
                new_x, new_blX = x_val, False
                x_changed = True
        else:
            if x_val > current_x:
                new_x, new_blX = x_val + eff_offset_x, True
                x_changed = True
            else:
                new_x, new_blX = x_val, False

    # --- Y (mesma lógica de antes) ---
    new_y = current_y
    new_blY = blY
    if "Y" in params:
        y_val = params["Y"]
        if offset_y > 0:
            if blY:
                if (y_val + offset_y) >= current_y:
                    new_y, new_blY = y_val + offset_y, True
                else:
                    new_y, new_blY = y_val, False
                    y_changed = True
            else:
                if y_val > current_y:
                    new_y, new_blY = y_val + offset_y, True
                    y_changed = True
                else:
                    new_y, new_blY = y_val, False
        else:
            new_y, new_blY = y_val, blY

    # gera linha de viagem ;BL se direção mudou e houve extrusão
    travel_tokens = None
    if has_extrusion and (x_changed or y_changed):
        travel_tokens = [tokens[0]]
        if "F" in params:
            travel_tokens.append("F" + str(int(params["F"])))
        # usa eff_offset_x e Y atual
        if "X" in params:
            travel_tokens.append(
                "X" + f"{(current_x - eff_offset_x) if blX else (current_x + eff_offset_x):.3f}"
            )
        if "Y" in params:
            travel_tokens.append("Y" + f"{current_y:.3f}")
        travel_tokens.append(";BL")

    # reconstrói tokens de extrusão com offset aplicado
    new_tokens = tokens.copy()
    if "X" in params:
        new_tokens[token_map["X"]] = "X" + f"{new_x:.3f}"
    if "Y" in params:
        new_tokens[token_map["Y"]] = "Y" + f"{new_y:.3f}"

    return new_tokens, new_x, new_y, new_blX, new_blY, travel_tokens, has_extrusion

def main():
    if len(sys.argv) < 2:
        print("Uso: backlash_compensator.py <arquivo.gcode> [idex|copy|mirror]")
        return

    mode = "idex"
    if len(sys.argv) >= 3 and sys.argv[2].lower() in ("idex","copy","mirror"):
        mode = sys.argv[2].lower()

    input_path = sys.argv[1]
    if not input_path.endswith(".gcode") or not os.path.isfile(input_path):
        print("Arquivo inválido ou não encontrado:", input_path)
        return

    offset_x_T0, offset_x_T1, offset_y = get_offsets()
    current_x = current_y = 0.0
    blX = blY = False
    absolute_mode = False
    current_tool = "T0"

    tmp = input_path + ".tmp"
    with open(input_path) as infile, open(tmp, "w") as outfile:
        for line in infile:
            tokens = parse_gcode_line(line)
            if not tokens:
                outfile.write(line)
                continue

            # troca de ferramenta
            if tokens[0] in ("T0","T1"):
                current_tool = tokens[0]
                outfile.write(line)
                continue

            # detecta modos absoluto/relativo
            if any(t.startswith("G90") for t in tokens):
                absolute_mode = True
                outfile.write(line); continue
            if any(t.startswith("G91") for t in tokens):
                absolute_mode = False
                outfile.write(line); continue
            if not absolute_mode:
                outfile.write(line); continue

            # processa movimentos
            if tokens[0].startswith(("G0","G1")):
                (new_tokens, new_x, new_y,
                 new_blX, new_blY,
                 travel_tokens, _) = process_line(
                    tokens, current_x, current_y, blX, blY,
                    offset_x_T0, offset_x_T1, offset_y,
                    current_tool, mode
                )
                if travel_tokens:
                    outfile.write(reconstruct_gcode_line(travel_tokens))
                outfile.write(reconstruct_gcode_line(new_tokens))
                current_x, current_y = new_x, new_y
                blX, blY = new_blX, new_blY
            else:
                outfile.write(line)

        outfile.write(f"; Compensado por backlash_compensator.py {version_code} – "
                      f"X_T0={offset_x_T0:.3f} X_T1={offset_x_T1:.3f} Y={offset_y:.3f} mode={mode}\n")

    os.rename(input_path, input_path + ".original")
    os.rename(tmp, input_path)
    print(f"Arquivo processado e sobrescrito (backup em .original): {input_path}")

if __name__ == "__main__":
    main()
