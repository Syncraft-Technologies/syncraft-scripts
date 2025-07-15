#!/usr/bin/env python3
import os
import sys

version_code = "o3HighMini0"
directoryPath = os.path.dirname(os.path.realpath(__file__))

def get_offsets():
    try:
        with open(os.path.join(directoryPath, "offsets.ini"), "r") as f:
            lines = f.readlines()
        if len(lines) >= 2:
            offset_x = float(lines[0].strip())
            offset_y = float(lines[1].strip())
            return offset_x, offset_y
    except Exception:
        pass
    return 0.0, 0.0  # fallback seguro

def parse_gcode_line(line):
    return line.rstrip("\n").split()

def reconstruct_gcode_line(tokens):
    return " ".join(tokens) + "\n"

def process_line(tokens, current_x, current_y, blX, blY, offset_x, offset_y):
    if not tokens or not (tokens[0].startswith("G0") or tokens[0].startswith("G1")):
        return tokens, current_x, current_y, blX, blY, None, False

    params = {}
    token_map = {}
    has_extrusion = False
    for i, token in enumerate(tokens):
        if token[0] in ["X", "Y", "Z", "E", "F"]:
            try:
                val = float(token[1:])
                params[token[0]] = val
                token_map[token[0]] = i
                if token[0] == "E":
                    has_extrusion = True
            except ValueError:
                pass

    if "X" not in params and "Y" not in params:
        return tokens, current_x, current_y, blX, blY, None, has_extrusion

    # Detectar mudança de direção
    x_changed = False
    y_changed = False

    new_x = current_x
    new_blX = blX
    if "X" in params:
        x_val = params["X"]
        if offset_x > 0:
            if blX:
                if (x_val + offset_x) >= current_x:
                    new_x = x_val + offset_x
                    new_blX = True
                else:
                    new_x = x_val
                    new_blX = False
                    x_changed = True
            else:
                if x_val > current_x:
                    new_x = x_val + offset_x
                    new_blX = True
                    x_changed = True
                else:
                    new_x = x_val
                    new_blX = False
        else:
            new_x = x_val
            new_blX = blX

    new_y = current_y
    new_blY = blY
    if "Y" in params:
        y_val = params["Y"]
        if offset_y > 0:
            if blY:
                if (y_val + offset_y) >= current_y:
                    new_y = y_val + offset_y
                    new_blY = True
                else:
                    new_y = y_val
                    new_blY = False
                    y_changed = True
            else:
                if y_val > current_y:
                    new_y = y_val + offset_y
                    new_blY = True
                    y_changed = True
                else:
                    new_y = y_val
                    new_blY = False
        else:
            new_y = y_val
            new_blY = blY

    # Somente inserir UMA única linha ;BL se houver mudança de direção E extrusão
    travel_tokens = None
    if has_extrusion and (x_changed or y_changed):
        travel_tokens = [tokens[0]]
        if "F" in params:
            travel_tokens.append("F" + str(int(params["F"])))
        # PARA ser fiel ao original: não aplicamos offset em Y no travel move,
        # pois o deslocamento de Y será aplicado na linha de extrusão real.
        if "X" in params:
            travel_tokens.append("X" + f"{(current_x - offset_x) if blX else (current_x + offset_x):.3f}")
        if "Y" in params:
            travel_tokens.append("Y" + f"{current_y:.3f}")   # <<<<<< SEM offset aqui
        travel_tokens.append(";BL")

    # Agora reconstruir os NEW_TOKENS com offset aplicado *na linha de extrusão real*
    new_tokens = tokens.copy()
    if "X" in params:
        new_tokens[token_map["X"]] = "X" + f"{new_x:.3f}"
    if "Y" in params:
        new_tokens[token_map["Y"]] = "Y" + f"{new_y:.3f}"

    return new_tokens, new_x, new_y, new_blX, new_blY, travel_tokens, has_extrusion

def main():
    if len(sys.argv) < 2:
        print("Uso: backlash_compensator.py <arquivo.gcode>")
        return

    input_path = sys.argv[1]
    if not input_path.endswith(".gcode") or not os.path.isfile(input_path):
        print("Arquivo inválido ou não encontrado:", input_path)
        return

    offset_x, offset_y = get_offsets()
    current_x, current_y = 0.0, 0.0
    blX, blY = False, False
    absolute_mode = False

    temp_path = input_path + ".tmp"
    with open(input_path, "r") as infile, open(temp_path, "w") as outfile:
        for line in infile:
            tokens = parse_gcode_line(line)
            if not tokens:
                outfile.write(line)
                continue

            if any(t.startswith("G90") for t in tokens):
                absolute_mode = True
                outfile.write(line)
                continue
            if any(t.startswith("G91") for t in tokens):
                absolute_mode = False
                outfile.write(line)
                continue
            if not absolute_mode:
                outfile.write(line)
                continue

            if tokens[0].startswith("G0") or tokens[0].startswith("G1"):
                new_tokens, new_x, new_y, new_blX, new_blY, travel_tokens, _ = process_line(
                    tokens, current_x, current_y, blX, blY, offset_x, offset_y
                )
                if travel_tokens:
                    outfile.write(reconstruct_gcode_line(travel_tokens))
                # Sempre escrevemos o new_tokens, mas sem duplicar duas linhas de “travel”
                outfile.write(reconstruct_gcode_line(new_tokens))
                current_x = new_x
                current_y = new_y
                blX = new_blX
                blY = new_blY
            else:
                outfile.write(line)

        outfile.write(f"; Compensado por backlash_compensator.py {version_code} – offset_x={offset_x:.3f} offset_y={offset_y:.3f}\\n")

    os.rename(input_path, input_path + ".original")
    os.rename(temp_path, input_path)
    print(f"Arquivo processado e sobrescrito (backup em .original): {input_path}")

if __name__ == "__main__":
    main()

