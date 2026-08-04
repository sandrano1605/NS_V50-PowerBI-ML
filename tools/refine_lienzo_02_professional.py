#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('.')
PAGE = ROOT / 'NS.Report/definition/pages/df1cb253a6314642a469'
VIS = PAGE / 'visuals'
MEDIDAS = ROOT / 'NS.SemanticModel/definition/tables/Medidas.tmdl'
EVIDENCE = ROOT / 'Docs/AUDITORIA_LIVE/latest/lienzo_02_professional_validation.json'

MEASURE_BLOCK = r'''
	/// Lectura ejecutiva dinámica del ingreso de pedidos en el contexto filtrado.
	measure 'IN Lectura Ejecutiva' =
			VAR TablaPedidos = ADDCOLUMNS(VALUES(Dim_Fecha[Dia_Semana]), "__Valor", CALCULATE([IN Pedidos]))
			VAR TablaLineas = ADDCOLUMNS(VALUES(Dim_Fecha[Dia_Semana]), "__Valor", CALCULATE([IN Líneas]))
			VAR TablaUnidades = ADDCOLUMNS(VALUES(Dim_Fecha[Dia_Semana]), "__Valor", CALCULATE([IN Unidades]))
			VAR TopPedidos = TOPN(1, FILTER(TablaPedidos, NOT ISBLANK([__Valor])), [__Valor], DESC, Dim_Fecha[Dia_Semana], ASC)
			VAR TopLineas = TOPN(1, FILTER(TablaLineas, NOT ISBLANK([__Valor])), [__Valor], DESC, Dim_Fecha[Dia_Semana], ASC)
			VAR TopUnidades = TOPN(1, FILTER(TablaUnidades, NOT ISBLANK([__Valor])), [__Valor], DESC, Dim_Fecha[Dia_Semana], ASC)
			VAR DiaPedidos = MAXX(TopPedidos, Dim_Fecha[Dia_Semana])
			VAR ValorPedidos = MAXX(TopPedidos, [__Valor])
			VAR DiaLineas = MAXX(TopLineas, Dim_Fecha[Dia_Semana])
			VAR ValorLineas = MAXX(TopLineas, [__Valor])
			VAR DiaUnidades = MAXX(TopUnidades, Dim_Fecha[Dia_Semana])
			VAR ValorUnidades = MAXX(TopUnidades, [__Valor])
			VAR PedidosTotal = [IN Pedidos]
			VAR PedidosDespues1430 = CALCULATE([IN Pedidos], KEEPFILTERS(Fact_Tracking[TRAMO_HORA_INGRESO] = "Después de 14:30"))
			VAR PorcDespues1430 = DIVIDE(PedidosDespues1430, PedidosTotal)
			VAR PromedioCierre = CALCULATE(AVERAGEX(VALUES(Dim_Fecha[Fecha]), [IN Pedidos]), KEEPFILTERS(Dim_Fecha[Momento_Mes] = "Cierre · últimos 7 DH"))
			VAR PromedioResto = CALCULATE(AVERAGEX(VALUES(Dim_Fecha[Fecha]), [IN Pedidos]), KEEPFILTERS(Dim_Fecha[Momento_Mes] = "Resto del mes"))
			VAR DeltaCierre = DIVIDE(PromedioCierre - PromedioResto, PromedioResto)
			VAR PedidosCierre = CALCULATE([IN Pedidos], KEEPFILTERS(Dim_Fecha[Momento_Mes] = "Cierre · últimos 7 DH"))
			VAR PedidosFesSaldoCierre = CALCULATE([IN Pedidos], KEEPFILTERS(Dim_Fecha[Momento_Mes] = "Cierre · últimos 7 DH"), KEEPFILTERS(Fact_Tracking[CLASIFICACION] IN {"FES", "FES + SALDO", "SALDO"}))
			VAR PorcFesSaldoCierre = DIVIDE(PedidosFesSaldoCierre, PedidosCierre)
			RETURN
				IF(
					ISBLANK(PedidosTotal),
					"Sin datos para los filtros seleccionados",
					"Días líderes · Pedidos: " & DiaPedidos & " (" & FORMAT(ValorPedidos, "#,0") & ")"
						& " · Líneas: " & DiaLineas & " (" & FORMAT(ValorLineas, "#,0") & ")"
						& " · Unidades: " & DiaUnidades & " (" & FORMAT(ValorUnidades, "#,0") & ")"
						& " | Después de 14:30: " & FORMAT(PorcDespues1430, "0.0%")
						& " | Cierre vs resto: " & FORMAT(DeltaCierre, "+0.0%;-0.0%;0.0%")
						& " · FES/Saldo en cierre: " & FORMAT(PorcFesSaldoCierre, "0.0%")
				)
		displayFolder: 04. Análisis Fuera SLA\Carga y SLA
		lineageTag: 61000000-0000-4000-8000-000000000107

'''


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def lit(value: str) -> dict:
    return {'expr': {'Literal': {'Value': value}}}


def card_json(name: str, measure: str, title: str, position: dict) -> dict:
    ref = f'Medidas.{measure}'
    return {
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json',
        'name': name,
        'position': position,
        'visual': {
            'visualType': 'cardVisual',
            'query': {'queryState': {'Data': {'projections': [{
                'field': {'Measure': {'Expression': {'SourceRef': {'Entity': 'Medidas'}}, 'Property': measure}},
                'queryRef': ref,
                'nativeQueryRef': title,
                'displayName': title,
            }]}}},
            'objects': {
                'value': [{'properties': {
                    'horizontalAlignment': lit("'center'"),
                    'fontSize': lit('22L'),
                    'fontColor': {'solid': {'color': lit("'#1B365D'")}},
                    'bold': lit('true'),
                }, 'selector': {'metadata': ref}}],
                'label': [{'properties': {'show': lit('false')}, 'selector': {'metadata': ref}}],
            },
            'visualContainerObjects': {
                'title': [{'properties': {
                    'show': lit('true'),
                    'text': lit(f"'{title}'"),
                    'alignment': lit("'center'"),
                    'fontSize': lit('9D'),
                    'fontFamily': lit("'Segoe UI Semibold'"),
                    'fontColor': {'solid': {'color': lit("'#535A65'")}},
                }}],
                'background': [{'properties': {
                    'show': lit('true'),
                    'color': {'solid': {'color': lit("'#FFFFFF'")}},
                    'transparency': lit('0D'),
                }}],
                'border': [{'properties': {
                    'show': lit('true'),
                    'color': {'solid': {'color': lit("'#CED9E5'")}},
                    'radius': lit('8D'),
                }}],
                'visualHeader': [{'properties': {'show': lit('false')}}],
            },
            'drillFilterOtherVisuals': True,
        },
        'filterConfig': {'filters': [{
            'name': f'{name}_m',
            'field': {'Measure': {'Expression': {'SourceRef': {'Entity': 'Medidas'}}, 'Property': measure}},
            'type': 'Advanced',
        }]},
    }


def insight_json() -> dict:
    measure = 'IN Lectura Ejecutiva'
    return {
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json',
        'name': 'in_nota_cierre',
        'position': {'x': 586, 'y': 150, 'z': 7000, 'height': 72, 'width': 990, 'tabOrder': 4151},
        'visual': {
            'visualType': 'tableEx',
            'query': {'queryState': {'Values': {'projections': [{
                'field': {'Measure': {'Expression': {'SourceRef': {'Entity': 'Medidas'}}, 'Property': measure}},
                'queryRef': f'Medidas.{measure}',
                'nativeQueryRef': 'Lectura ejecutiva',
                'displayName': 'Lectura ejecutiva',
            }]}}},
            'objects': {
                'grid': [{'properties': {'rowPadding': lit('1L')}}],
                'columnHeaders': [{'properties': {
                    'fontSize': lit('1L'),
                    'fontColor': {'solid': {'color': lit("'#F4F7FB'")}},
                    'backColor': {'solid': {'color': lit("'#F4F7FB'")}},
                }}],
                'total': [{'properties': {'totals': lit('false')}}],
                'values': [{'properties': {
                    'fontSize': lit('9L'),
                    'wordWrap': lit('true'),
                    'fontColorPrimary': {'solid': {'color': lit("'#1B365D'")}},
                    'fontColorSecondary': {'solid': {'color': lit("'#1B365D'")}},
                    'backColorPrimary': {'solid': {'color': lit("'#F4F7FB'")}},
                    'backColorSecondary': {'solid': {'color': lit("'#F4F7FB'")}},
                }}],
            },
            'visualContainerObjects': {
                'title': [{'properties': {
                    'show': lit('true'),
                    'text': lit("'Lectura ejecutiva del ingreso'"),
                    'alignment': lit("'left'"),
                    'fontSize': lit('9D'),
                    'fontFamily': lit("'Segoe UI Semibold'"),
                    'fontColor': {'solid': {'color': lit("'#1B365D'")}},
                }}],
                'background': [{'properties': {
                    'show': lit('true'),
                    'color': {'solid': {'color': lit("'#F4F7FB'")}},
                    'transparency': lit('0D'),
                }}],
                'border': [{'properties': {
                    'show': lit('true'),
                    'color': {'solid': {'color': lit("'#CED9E5'")}},
                    'radius': lit('8D'),
                }}],
                'visualHeader': [{'properties': {'show': lit('false')}}],
                'padding': [{'properties': {
                    'top': lit('2L'), 'bottom': lit('2L'), 'left': lit('6L'), 'right': lit('6L')
                }}],
            },
            'drillFilterOtherVisuals': True,
        },
        'filterConfig': {'filters': [{
            'name': 'in_nota_cierre_m',
            'field': {'Measure': {'Expression': {'SourceRef': {'Entity': 'Medidas'}}, 'Property': measure}},
            'type': 'Advanced',
        }]},
    }


def enable_labels_and_title(path: Path, title: str, position: dict | None = None, z: int | None = None) -> None:
    data = load(path)
    if position:
        data['position'].update(position)
    if z is not None:
        data['position']['z'] = z
    objects = data['visual'].setdefault('objects', {})
    labels = objects.setdefault('labels', [{'properties': {}}])
    labels[0].setdefault('properties', {})['show'] = lit('true')
    title_props = data['visual'].setdefault('visualContainerObjects', {}).setdefault('title', [{'properties': {}}])[0].setdefault('properties', {})
    title_props['show'] = lit('true')
    title_props['text'] = lit(f"'{title}'")
    title_props['fontSize'] = lit('10D')
    title_props['fontFamily'] = lit("'Segoe UI Semibold'")
    title_props['fontColor'] = {'solid': {'color': lit("'#1B365D'")}}
    data['visual']['visualContainerObjects'].setdefault('visualHeader', [{'properties': {}}])[0]['properties']['show'] = lit('false')
    save(path, data)


def main() -> None:
    text = MEDIDAS.read_text(encoding='utf-8-sig')
    if "measure 'IN Lectura Ejecutiva'" not in text:
        marker = '\tcolumn __Medida'
        if marker not in text:
            raise RuntimeError('No se encontró el marcador column __Medida')
        text = text.replace(marker, MEASURE_BLOCK + marker, 1)
        MEDIDAS.write_text(text, encoding='utf-8', newline='\n')

    cards = [
        ('table_9601cabf413a41', 'IN Pedidos', 'Pedidos ingresados', {'x': 24, 'y': 150, 'z': 7000, 'height': 72, 'width': 170, 'tabOrder': 7024}),
        ('table_62c6c02944b14e', 'IN Líneas', 'Líneas ingresadas', {'x': 206, 'y': 150, 'z': 7000, 'height': 72, 'width': 170, 'tabOrder': 7206}),
        ('table_bad13c26c1d64f', 'IN Unidades', 'Unidades ingresadas', {'x': 388, 'y': 150, 'z': 7000, 'height': 72, 'width': 170, 'tabOrder': 7388}),
    ]
    for name, measure, title, pos in cards:
        save(VIS / name / 'visual.json', card_json(name, measure, title, pos))

    save(VIS / 'in_nota_cierre' / 'visual.json', insight_json())

    enable_labels_and_title(
        VIS / 'chart_924aca87b5094c' / 'visual.json',
        'Disponibilidad para Logística por día · % hasta/después de 14:30',
    )

    common_pos = {'x': 24, 'y': 516, 'height': 392, 'width': 1552}
    enable_labels_and_title(
        VIS / 'in_chart_pedidos_dia_mes' / 'visual.json',
        'Pedidos por día del mes · barras por flujo · línea promedio',
        common_pos,
        12000,
    )
    enable_labels_and_title(
        VIS / 'in_chart_lineas_dia_mes' / 'visual.json',
        'Líneas por día del mes · barras por flujo · línea promedio',
        common_pos,
        11000,
    )
    enable_labels_and_title(
        VIS / 'in_chart_unidades_dia_mes' / 'visual.json',
        'Unidades por día del mes · barras por flujo · línea promedio',
        common_pos,
        10000,
    )

    expected = {
        'measure': "measure 'IN Lectura Ejecutiva'" in MEDIDAS.read_text(encoding='utf-8-sig'),
        'cards': {},
        'charts': {},
        'business_questions': {
            'Q1': 'Matriz + lectura ejecutiva con día líder para pedidos, líneas y unidades',
            'Q2': 'Gráfico 100% con etiquetas + porcentaje después de 14:30 en lectura ejecutiva',
            'Q3': 'Gráfico mensual con flujo/promedio + delta cierre vs resto y peso FES/Saldo',
        },
        'errors': [],
    }
    for name, _, _, _ in cards:
        data = load(VIS / name / 'visual.json')
        expected['cards'][name] = data['visual']['visualType']
        if data['visual']['visualType'] != 'cardVisual':
            expected['errors'].append(f'{name}: no es cardVisual')
    for name in ['chart_924aca87b5094c', 'in_chart_pedidos_dia_mes', 'in_chart_lineas_dia_mes', 'in_chart_unidades_dia_mes']:
        data = load(VIS / name / 'visual.json')
        show = data['visual']['objects']['labels'][0]['properties']['show']['expr']['Literal']['Value']
        expected['charts'][name] = {'labels': show, 'position': data['position']}
        if show != 'true':
            expected['errors'].append(f'{name}: etiquetas no activadas')
    positions = [expected['charts'][n]['position'] for n in ['in_chart_pedidos_dia_mes', 'in_chart_lineas_dia_mes', 'in_chart_unidades_dia_mes']]
    for key in ['x', 'y', 'height', 'width']:
        if len({p[key] for p in positions}) != 1:
            expected['errors'].append(f'Los gráficos no comparten {key}')
    expected['status'] = 'VERDE' if not expected['errors'] else 'ROJO'
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if expected['status'] != 'VERDE':
        raise SystemExit(json.dumps(expected, ensure_ascii=False, indent=2))
    print(json.dumps(expected, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
