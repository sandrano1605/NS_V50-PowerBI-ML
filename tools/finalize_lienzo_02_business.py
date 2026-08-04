from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIDAS = ROOT / "NS.SemanticModel/definition/tables/Medidas.tmdl"
TRACKING = ROOT / "NS.SemanticModel/definition/tables/Fact_Tracking.tmdl"
INSTRUCTION = ROOT / "Docs/AUDITORIA_LIVE/LLM_LOCAL_CIERRE_LIENZO_02.md"
VALIDATION = ROOT / "Docs/AUDITORIA_LIVE/latest/lienzo_02_business_fix_validation.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8")


def replace_measure(text: str) -> str:
    comment = "\t/// Lectura ejecutiva dinámica del ingreso de pedidos en el contexto filtrado."
    start = text.find(comment)
    if start < 0:
        raise RuntimeError("No se encontró el inicio de IN Lectura Ejecutiva")

    measure_start = text.find("\tmeasure 'IN Lectura Ejecutiva' =", start)
    if measure_start < 0:
        raise RuntimeError("No se encontró la medida IN Lectura Ejecutiva")

    candidates = [
        text.find("\n\tmeasure ", measure_start + 10),
        text.find("\n\tannotation ", measure_start + 10),
        text.find("\n\tpartition ", measure_start + 10),
    ]
    candidates = [value for value in candidates if value >= 0]
    end = min(candidates) if candidates else len(text)

    block = r'''	/// Lectura ejecutiva dinámica del ingreso de pedidos en el contexto filtrado.
	/// Q2 separa cobertura de hora y porcentaje posterior al corte sobre casos medibles.
	/// Q3 compara promedios diarios de cierre y resto, no totales de períodos de distinta duración.
	measure 'IN Lectura Ejecutiva' =
			VAR TablaPedidos =
				ADDCOLUMNS(
					VALUES(Dim_Fecha[Dia_Semana]),
					"__Valor", CALCULATE([IN Pedidos])
				)
			VAR TablaLineas =
				ADDCOLUMNS(
					VALUES(Dim_Fecha[Dia_Semana]),
					"__Valor", CALCULATE([IN Líneas])
				)
			VAR TablaUnidades =
				ADDCOLUMNS(
					VALUES(Dim_Fecha[Dia_Semana]),
					"__Valor", CALCULATE([IN Unidades])
				)
			VAR TopPedidos =
				TOPN(
					1,
					FILTER(TablaPedidos, NOT ISBLANK([__Valor])),
					[__Valor], DESC,
					Dim_Fecha[Dia_Semana], ASC
				)
			VAR TopLineas =
				TOPN(
					1,
					FILTER(TablaLineas, NOT ISBLANK([__Valor])),
					[__Valor], DESC,
					Dim_Fecha[Dia_Semana], ASC
				)
			VAR TopUnidades =
				TOPN(
					1,
					FILTER(TablaUnidades, NOT ISBLANK([__Valor])),
					[__Valor], DESC,
					Dim_Fecha[Dia_Semana], ASC
				)
			VAR DiaPedidos = MAXX(TopPedidos, Dim_Fecha[Dia_Semana])
			VAR DiaLineas = MAXX(TopLineas, Dim_Fecha[Dia_Semana])
			VAR DiaUnidades = MAXX(TopUnidades, Dim_Fecha[Dia_Semana])
			VAR ValorPedidos = MAXX(TopPedidos, [__Valor])
			VAR ValorLineas = MAXX(TopLineas, [__Valor])
			VAR ValorUnidades = MAXX(TopUnidades, [__Valor])

			VAR PedidosTotal = [IN Pedidos]
			VAR PedidosHasta1430 =
				CALCULATE(
					[IN Pedidos],
					KEEPFILTERS(Fact_Tracking[TRAMO_HORA_INGRESO] = "Hasta 14:30")
				)
			VAR PedidosDespues1430 =
				CALCULATE(
					[IN Pedidos],
					KEEPFILTERS(Fact_Tracking[TRAMO_HORA_INGRESO] = "Después de 14:30")
				)
			VAR PedidosSinHora =
				CALCULATE(
					[IN Pedidos],
					KEEPFILTERS(Fact_Tracking[TRAMO_HORA_INGRESO] = "Sin hora válida")
				)
			VAR PedidosConHora = PedidosHasta1430 + PedidosDespues1430
			VAR CoberturaHora = DIVIDE(PedidosConHora, PedidosTotal)
			VAR PorcDespuesMedibles = DIVIDE(PedidosDespues1430, PedidosConHora)
			VAR PorcSinHora = DIVIDE(PedidosSinHora, PedidosTotal)

			VAR PedidosCierre =
				CALCULATE(
					[IN Pedidos],
					REMOVEFILTERS(Dim_Fecha[Momento_Mes]),
					Dim_Fecha[Momento_Mes] = "Cierre · últimos 7 DH"
				)
			VAR PedidosResto =
				CALCULATE(
					[IN Pedidos],
					REMOVEFILTERS(Dim_Fecha[Momento_Mes]),
					Dim_Fecha[Momento_Mes] = "Resto del mes"
				)
			VAR DiasCierre =
				CALCULATE(
					COUNTROWS(
						FILTER(
							VALUES(Dim_Fecha[Fecha]),
							NOT ISBLANK(CALCULATE([IN Pedidos]))
						)
					),
					REMOVEFILTERS(Dim_Fecha[Momento_Mes]),
					Dim_Fecha[Momento_Mes] = "Cierre · últimos 7 DH"
				)
			VAR DiasResto =
				CALCULATE(
					COUNTROWS(
						FILTER(
							VALUES(Dim_Fecha[Fecha]),
							NOT ISBLANK(CALCULATE([IN Pedidos]))
						)
					),
					REMOVEFILTERS(Dim_Fecha[Momento_Mes]),
					Dim_Fecha[Momento_Mes] = "Resto del mes"
				)
			VAR PromedioCierre = DIVIDE(PedidosCierre, DiasCierre)
			VAR PromedioResto = DIVIDE(PedidosResto, DiasResto)
			VAR DeltaCierre = DIVIDE(PromedioCierre - PromedioResto, PromedioResto)
			VAR PedidosFesSaldoCierre =
				CALCULATE(
					[IN Pedidos],
					REMOVEFILTERS(Dim_Fecha[Momento_Mes]),
					Dim_Fecha[Momento_Mes] = "Cierre · últimos 7 DH",
					KEEPFILTERS(Fact_Tracking[CLASIFICACION] IN {"FES", "FES + SALDO", "SALDO"})
				)
			VAR PorcFesSaldoCierre = DIVIDE(PedidosFesSaldoCierre, PedidosCierre)

			VAR TablaDiaMesUnidades =
				ADDCOLUMNS(
					VALUES(Dim_Fecha[Dia_Mes]),
					"__Unidades", CALCULATE([IN Unidades])
				)
			VAR TopDiaMesUnidades =
				TOPN(
					1,
					FILTER(TablaDiaMesUnidades, NOT ISBLANK([__Unidades])),
					[__Unidades], DESC,
					Dim_Fecha[Dia_Mes], ASC
				)
			VAR DiaPicoUnidades = MAXX(TopDiaMesUnidades, Dim_Fecha[Dia_Mes])
			VAR UnidadesPico = MAXX(TopDiaMesUnidades, [__Unidades])
			VAR PorcUnidadesPico = DIVIDE(UnidadesPico, [IN Unidades])

			RETURN
				IF(
					ISBLANK(PedidosTotal),
					"Sin datos para los filtros seleccionados",
					"Días líderes · Pedidos: " & DiaPedidos & " (" & FORMAT(ValorPedidos, "#,0") & ")"
						& " · Líneas: " & DiaLineas & " (" & FORMAT(ValorLineas, "#,0") & ")"
						& " · Unidades: " & DiaUnidades & " (" & FORMAT(ValorUnidades, "#,0") & ")"
						& UNICHAR(10)
						& "Hora válida: " & FORMAT(CoberturaHora, "0.0%")
						& " · Después de 14:30 sobre medibles: " & FORMAT(PorcDespuesMedibles, "0.0%")
						& " · Sin hora: " & FORMAT(PorcSinHora, "0.0%")
						& UNICHAR(10)
						& "Cierre vs resto (promedio diario): " & FORMAT(PromedioCierre, "#,0.0")
						& " vs " & FORMAT(PromedioResto, "#,0.0")
						& " (" & FORMAT(DeltaCierre, "+0.0%;-0.0%;0.0%") & ")"
						& " · FES/Saldo: " & FORMAT(PorcFesSaldoCierre, "0.0%")
						& " · Día pico unidades: " & FORMAT(DiaPicoUnidades, "0")
						& " (" & FORMAT(PorcUnidadesPico, "0.0%") & ")"
				)
		displayFolder: 04. Análisis Fuera SLA\Carga y SLA
		lineageTag: 61000000-0000-4000-8000-000000000107
'''.strip("\n")

    return text[:start] + block + "\n\n" + text[end + 1 :]


def fix_tracking(text: str) -> str:
    tramo_anchor = (
        "\tcolumn TRAMO_HORA_INGRESO\n"
        "\t\tdataType: string\n"
        "\t\tlineageTag: 26000000-0000-4000-8000-000000001044\n"
        "\t\tsummarizeBy: none\n"
        "\t\tsourceColumn: TRAMO_HORA_INGRESO\n"
    )
    tramo_fixed = tramo_anchor + "\t\tsortByColumn: ORDEN_TRAMO_HORA_INGRESO\n"
    if tramo_anchor in text and "\t\tsortByColumn: ORDEN_TRAMO_HORA_INGRESO" not in text:
        text = text.replace(tramo_anchor, tramo_fixed, 1)

    old_end = "\t\t\t\tin\n\t\t\t\t    Resultado"
    new_end = (
        "\t\t\t\t    // Fact_Tracking debe conservar exactamente una fila por pedido.\n"
        "\t\t\t\t    ResultadoUnico = Table.Distinct(Resultado, {\"PED_NUMERO_PEDIDO\"})\n"
        "\t\t\t\tin\n"
        "\t\t\t\t    ResultadoUnico"
    )
    if "ResultadoUnico = Table.Distinct" not in text:
        if old_end not in text:
            raise RuntimeError("No se encontró el cierre de la partición Fact_Tracking")
        text = text.replace(old_end, new_end, 1)
    return text


def build_instruction() -> str:
    return """# LLM local · Cierre definitivo lienzo 02

## Rol

La solución ya está corregida. No modificar DAX, Power Query, TMDL, JSON, medidas, visuales, bookmarks ni botones.

Ejecutar únicamente: recuperar rama, refrescar, probar, reconciliar, diagnosticar y publicar evidencia.

## Controles obligatorios

### Modelo

1. `Fact_Tracking` debe tener una fila por `PED_NUMERO_PEDIDO`.
2. Informar filas, pedidos distintos y duplicados de `Fact_Tracking`.
3. Comparar pedidos de `Fact_Tracking` contra `Fact_Pedidos_Auditoria` con `EXCEPT` en ambos sentidos.
4. Si existe diferencia, listar los pedidos y determinar si corresponde a cambio de la fuente durante el refresh. Repetir un segundo refresh antes de clasificarlo como defecto.
5. No declarar VERDE mientras exista una diferencia no explicada.

### Q1

Reconciliar día líder y valor para pedidos, líneas y unidades.

### Q2

Publicar cuatro cifras:

- cobertura de hora válida = `(Hasta 14:30 + Después 14:30) / Total`;
- porcentaje hasta 14:30 sobre pedidos con hora válida;
- porcentaje después de 14:30 sobre pedidos con hora válida;
- porcentaje sin hora válida sobre el total.

La lectura ejecutiva y la consulta independiente deben coincidir.

### Q3

No comparar totales de períodos con distinta cantidad de días.

Publicar:

- cantidad de días con ingreso en cierre;
- pedidos de cierre;
- promedio diario de cierre;
- cantidad de días con ingreso en resto;
- pedidos del resto;
- promedio diario del resto;
- delta entre promedios diarios;
- participación FES/Saldo en cierre;
- día pico de unidades y participación sobre las unidades del período.

### Botones y filtros

La prueba debe ser real en Power BI Desktop, no solo estructural:

1. Seleccionar mes, canal distinto de 43/45, flujo, zona, responsable y momento del mes.
2. Pulsar los tres botones.
3. Confirmar exactamente un gráfico visible por clic.
4. Confirmar que ningún filtro cambia.
5. Cambiar mes y canal, repetir.
6. Cerrar, reabrir y repetir.

## Evidencia

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_cierre_definitivo/
```

Archivos mínimos:

```text
00_git.txt
01_refresh_1.txt
02_refresh_2.txt
03_tracking_vs_master.csv
04_q1_dia_semana.csv
05_q2_cobertura_horaria.csv
06_q3_promedios_diarios.csv
07_q3_flujo_y_pico_unidades.csv
08_botones_prueba_real.csv
09_filtros_persistencia.csv
10_calidad_visual.txt
11_regresiones.txt
12_incoherencias.csv
RESULTADO.md
manifest.json
```

`RESULTADO.md` debe responder Q1, Q2 y Q3 con cifras y explicar cualquier diferencia entre Tracking y master.

Commit permitido:

```text
audit(lienzo-02): validar cierre definitivo
```

Versionar solamente la carpeta de evidencia.
"""


def main() -> None:
    medidas_before = read(MEDIDAS)
    tracking_before = read(TRACKING)

    medidas_after = replace_measure(medidas_before)
    tracking_after = fix_tracking(tracking_before)

    write(MEDIDAS, medidas_after)
    write(TRACKING, tracking_after)
    write(INSTRUCTION, build_instruction())

    checks = {
        "lectura_hora_cobertura": "Hora válida:" in medidas_after,
        "lectura_despues_medibles": "Después de 14:30 sobre medibles" in medidas_after,
        "lectura_promedio_diario": "Cierre vs resto (promedio diario)" in medidas_after,
        "lectura_pico_unidades": "Día pico unidades" in medidas_after,
        "tracking_una_fila": "ResultadoUnico = Table.Distinct(Resultado, {\"PED_NUMERO_PEDIDO\"})" in tracking_after,
        "tracking_sort_hora": "sortByColumn: ORDEN_TRAMO_HORA_INGRESO" in tracking_after,
        "instruccion_prueba_real": "prueba debe ser real" in build_instruction(),
    }
    status = "VERDE" if all(checks.values()) else "ROJO"
    payload = {"status": status, "checks": checks, "errors": [k for k, v in checks.items() if not v]}
    write(VALIDATION, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    if status != "VERDE":
        raise SystemExit(json.dumps(payload, ensure_ascii=False))

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
