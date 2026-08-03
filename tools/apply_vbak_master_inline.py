#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "NS.SemanticModel/definition/tables/Fact_Pedidos_Auditoria.tmdl"
BLOCK = ROOT / "PowerQuery/VBAK_APPEND/06_MASTER_APPEND_INLINE_ACTIVE.pq"
EVIDENCE = ROOT / "Docs/AUDITORIA_LIVE/latest/vbak_master_inline_validation.json"
PREFIX = "\t\t\t\t"

OLD_TAIL = (
    PREFIX + '    #"Filas ordenadas" = Table.Sort(FiltradoCanalesMayoristas,{{"PED_FECHA_HORA", Order.Descending}})\n'
    + PREFIX + "in\n"
    + PREFIX + '    #"Filas ordenadas"\n'
)


def balance_m(text: str) -> list[str]:
    errors: list[str] = []
    pairs = {')': '(', ']': '[', '}': '{'}
    stack: list[tuple[str, int]] = []
    in_string = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '"':
            if in_string and i + 1 < len(text) and text[i + 1] == '"':
                i += 2
                continue
            in_string = not in_string
        elif not in_string:
            if ch in '([{':
                stack.append((ch, i))
            elif ch in ')]}':
                if not stack or stack[-1][0] != pairs[ch]:
                    errors.append(f"Cierre desbalanceado {ch} en posición {i}")
                    break
                stack.pop()
        i += 1
    if in_string:
        errors.append("Cadena M sin cierre")
    if stack:
        errors.append(f"Delimitadores M sin cierre: {stack[-5:]}")
    return errors


def main() -> int:
    original = MASTER.read_text(encoding="utf-8-sig")
    block = BLOCK.read_text(encoding="utf-8-sig").rstrip("\n")

    if original.count(OLD_TAIL) != 1:
        raise RuntimeError(f"Tail esperado encontrado {original.count(OLD_TAIL)} veces")
    if "\nin\n" in block or block.lstrip().startswith("in "):
        raise RuntimeError("El bloque inline no debe contener cláusula in")
    if "VBAK_APPEND_ACTIVO_LOCAL = true" not in block:
        raise RuntimeError("El append inline no está activo")
    if "ES_FES_VBFA" not in block or "JoinKind.LeftAnti" not in block:
        raise RuntimeError("Faltan barreras VBFA o anti-join")

    prefixed_block = "\n".join(PREFIX + line for line in block.splitlines())
    replacement = (
        PREFIX + '    #"Filas ordenadas" = Table.Sort(FiltradoCanalesMayoristas,{{"PED_FECHA_HORA", Order.Descending}}),\n'
        + prefixed_block + "\n"
        + PREFIX + "in\n"
        + PREFIX + "    ResultadoVBAK\n"
    )
    updated = original.replace(OLD_TAIL, replacement, 1)

    errors: list[str] = []
    if updated.count("partition Fact_Pedidos_Auditoria = m") != 1:
        errors.append("Cantidad inválida de particiones master")
    if updated.count("VBAK_APPEND_ACTIVO_LOCAL = true") != 1:
        errors.append("El interruptor inline no quedó exactamente una vez")
    if updated.count(PREFIX + "    ResultadoVBAK\n") != 1:
        errors.append("ResultadoVBAK final ausente o duplicado")
    if OLD_TAIL in updated:
        errors.append("Persistió el tail anterior")
    if "VBAK SIN ZART" not in updated:
        errors.append("Falta marcador de trazabilidad")
    if "ES_FES_VBFA" not in updated:
        errors.append("Falta exclusión FES VBFA")
    errors.extend(balance_m(block))

    result = {
        "status": "VERDE" if not errors else "ROJO",
        "master": str(MASTER.relative_to(ROOT)),
        "block": str(BLOCK.relative_to(ROOT)),
        "append_active": True,
        "excludes_fes_vbfa": "ES_FES_VBFA" in block,
        "uses_left_anti": "JoinKind.LeftAnti" in block,
        "marker": "VBAK SIN ZART",
        "errors": errors,
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    MASTER.write_text(updated, encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
