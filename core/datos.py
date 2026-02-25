"""
datos.py — Parseo del CSV de cálculos hidráulicos.

Lee CALCULOS_HIDRAULICOS.csv y extrae los datos organizados
en DataFrames de pandas para cada sección del proyecto.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def _limpiar_numero(valor: str) -> float:
    """Convierte un string con formato latino (1.030,49) a float (1030.49)."""
    if pd.isna(valor) or str(valor).strip() == '':
        return np.nan
    s = str(valor).strip()
    # Quitar puntos de miles y reemplazar coma decimal por punto
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return np.nan


def cargar_csv(ruta: str | Path | None = None) -> list[list[str]]:
    """Lee el CSV crudo y devuelve una lista de filas (cada fila es lista de strings)."""
    if ruta is None:
        ruta = Path(__file__).parent.parent / "CALCULOS_HIDRAULICOS.csv"
    ruta = Path(ruta)

    filas = []
    with open(ruta, 'r', encoding='utf-8') as f:
        for linea in f:
            # Separar por punto y coma
            campos = linea.rstrip('\n').split(';')
            filas.append(campos)
    return filas


def extraer_perfil_terreno(filas: list[list[str]]) -> pd.DataFrame:
    """
    Extrae el perfil topográfico del terreno (filas 1-8 del CSV, índice 1-8).
    Retorna DataFrame con: altura_mapa, largo_mapa, hipotenusa_mapa,
    altura_real, distancia_acumulada, distancia, altitud.
    """
    datos = []
    for i in range(1, 9):  # filas 1-8 (después del encabezado)
        fila = filas[i]
        datos.append({
            'altura_mapa': _limpiar_numero(fila[0]),
            'largo_mapa': _limpiar_numero(fila[1]),
            'hipotenusa_mapa': _limpiar_numero(fila[2]),
            'altura_real': _limpiar_numero(fila[3]),
            'distancia_acumulada': _limpiar_numero(fila[4]),
            'distancia': _limpiar_numero(fila[5]),
            'altitud': _limpiar_numero(fila[6]),
        })
    return pd.DataFrame(datos)


def extraer_parametros_globales(filas: list[list[str]]) -> dict:
    """Extrae parámetros globales: escala, distancia río, etc."""
    return {
        'escala': _limpiar_numero(filas[15][1]),  # fila "Escala"
        'distancia_rio_mapa': _limpiar_numero(filas[11][2]),  # 7.75
        'montaña_a_tierra': _limpiar_numero(filas[12][2]),  # 0.46
        'total_montaña': _limpiar_numero(filas[13][2]),  # 7.29
        'espacio_tierra_rio': _limpiar_numero(filas[17][2]),  # 87.50 m
        'distancia_total': _limpiar_numero(filas[34][2]),  # 3433.93 m
        'num_bombeos': _limpiar_numero(filas[35][2]),  # 7
        'num_depositos': _limpiar_numero(filas[36][2]),  # 12
    }


def extraer_resumen_tramos(filas: list[list[str]]) -> pd.DataFrame:
    """
    Extrae tabla resumen de tramos 1-7 (filas 21-27).
    Columnas: tramo, distancia, altura, pendiente, longitud_tuberia.
    """
    datos = []
    for i in range(21, 28):
        fila = filas[i]
        datos.append({
            'tramo': int(_limpiar_numero(fila[0])),
            'distancia': _limpiar_numero(fila[1]),
            'altura': _limpiar_numero(fila[2]),
            'pendiente': _limpiar_numero(fila[3]),
            'longitud_tuberia': _limpiar_numero(fila[4]),
        })
    return pd.DataFrame(datos)


def extraer_tramo_8_distancias(filas: list[list[str]]) -> pd.DataFrame:
    """Extrae las sub-distancias del tramo 8 (filas 85-92)."""
    nombres = []
    for i in range(85, 92):
        fila = filas[i]
        nombres.append({
            'segmento': fila[0].strip() if fila[0].strip() else '',
            'distancia': _limpiar_numero(fila[1]),
            'acumulado': _limpiar_numero(fila[2]),
            'altura': _limpiar_numero(fila[3]),
        })
    return pd.DataFrame(nombres)


def extraer_accesorios_tramo(filas: list[list[str]], col_inicio: int,
                              fila_inicio: int, fila_fin: int) -> pd.DataFrame:
    """
    Extrae la tabla de accesorios de un tramo dado el rango de columnas y filas.
    """
    datos = []
    for i in range(fila_inicio, fila_fin):
        fila = filas[i]
        if col_inicio + 3 < len(fila):
            nombre = fila[col_inicio].strip() if fila[col_inicio].strip() else None
            if nombre and nombre not in ('Accesorios', 'Accesorios por estación'):
                cantidad = _limpiar_numero(fila[col_inicio + 1])
                k_valor = _limpiar_numero(fila[col_inicio + 2])
                carga = _limpiar_numero(fila[col_inicio + 3])
                if not np.isnan(cantidad):
                    datos.append({
                        'nombre': nombre,
                        'cantidad': int(cantidad),
                        'K': k_valor,
                        'carga_m': carga,
                    })
    return pd.DataFrame(datos) if datos else pd.DataFrame(
        columns=['nombre', 'cantidad', 'K', 'carga_m']
    )


def extraer_accesorios_tramo_8(filas: list[list[str]]) -> pd.DataFrame:
    """Extrae accesorios del tramo 8 (filas 98-103, columnas 5-8)."""
    return extraer_accesorios_tramo(filas, col_inicio=5, fila_inicio=98, fila_fin=104)


def extraer_datos_completos() -> dict:
    """
    Función principal: carga y organiza todos los datos del CSV.
    
    Retorna un diccionario con:
    - 'perfil_terreno': DataFrame del perfil topográfico
    - 'parametros': dict con parámetros globales
    - 'resumen_tramos': DataFrame resumen de 7 tramos
    - 'tramo_8_distancias': DataFrame sub-distancias tramo 8
    - 'tramos_detalle': dict con datos detallados por tramo (1-8)
    """
    filas = cargar_csv()
    
    perfil = extraer_perfil_terreno(filas)
    parametros = extraer_parametros_globales(filas)
    resumen = extraer_resumen_tramos(filas)
    tramo8_dist = extraer_tramo_8_distancias(filas)
    
    # Extraer datos detallados por tramo (columnas del CSV en bloques de 5)
    tramos_detalle = {}
    
    # Tramos 1-7: cada uno ocupa 5 columnas (cols 0-4, 5-9, 10-14, 15-19, 20-24, 25-29, 30-33)
    for t in range(1, 8):
        col_base = (t - 1) * 5
        detalle = {
            'pendiente': _limpiar_numero(filas[43][col_base + 1]),
            'densidad': _limpiar_numero(filas[43][col_base + 3]),
            'caudal': _limpiar_numero(filas[44][col_base + 1]),
            'viscosidad': _limpiar_numero(filas[44][col_base + 3]),
            'longitud_tuberia': _limpiar_numero(filas[45][col_base + 1]),
            'rugosidad': _limpiar_numero(filas[45][col_base + 3]),
            'diametro': _limpiar_numero(filas[46][col_base + 1]),
            'area': _limpiar_numero(filas[48][col_base + 1]),
            'velocidad': _limpiar_numero(filas[49][col_base + 1]),
            'carga_cinetica': _limpiar_numero(filas[50][col_base + 1]),
            'reynolds': _limpiar_numero(filas[51][col_base + 1]),
            'f_colebrook': _limpiar_numero(filas[52][col_base + 1]),
            'f_haaland': _limpiar_numero(filas[53][col_base + 1]),
            'perdidas_darcy_crane': _limpiar_numero(filas[54][col_base + 1]),
            'perdidas_darcy_haaland': _limpiar_numero(filas[55][col_base + 1]),
        }
        # Accesorios
        detalle['accesorios'] = extraer_accesorios_tramo(
            filas, col_inicio=col_base, fila_inicio=58, fila_fin=63
        )
        tramos_detalle[t] = detalle
    
    # Datos de potencia y carga por tramo (extraídos manualmente del CSV)
    # Tramo 1
    tramos_detalle[1]['z'] = 100.0
    tramos_detalle[1]['carga_total'] = 102.35
    tramos_detalle[1]['potencia_kw'] = 25.05
    tramos_detalle[1]['potencia_hp'] = 33.59
    tramos_detalle[1]['num_estaciones'] = 1
    tramos_detalle[1]['tipo'] = 'bomba'
    
    # Tramo 2
    tramos_detalle[2]['z'] = 100.0
    tramos_detalle[2]['carga_total_estacion'] = 101.65
    tramos_detalle[2]['carga_total'] = 203.30
    tramos_detalle[2]['potencia_kw'] = 24.88
    tramos_detalle[2]['potencia_hp'] = 33.36
    tramos_detalle[2]['num_estaciones'] = 2
    tramos_detalle[2]['tipo'] = 'bomba'
    
    # Tramo 3
    tramos_detalle[3]['z'] = 100.0
    tramos_detalle[3]['carga_total_estacion'] = 101.58
    tramos_detalle[3]['carga_total'] = 203.15
    tramos_detalle[3]['potencia_kw'] = 31.08
    tramos_detalle[3]['potencia_hp'] = 41.68
    tramos_detalle[3]['num_estaciones'] = 2
    tramos_detalle[3]['tipo'] = 'bomba'
    
    # Tramo 4
    tramos_detalle[4]['z'] = 0.0
    tramos_detalle[4]['carga_total'] = 2.89
    tramos_detalle[4]['potencia_kw'] = 0.88
    tramos_detalle[4]['potencia_hp'] = 1.19
    tramos_detalle[4]['num_estaciones'] = 1
    tramos_detalle[4]['tipo'] = 'bomba'
    
    # Tramo 5
    tramos_detalle[5]['z'] = 0.0
    tramos_detalle[5]['carga_total_estacion'] = 1.43
    tramos_detalle[5]['carga_total'] = 2.87
    tramos_detalle[5]['potencia_kw'] = 0.0
    tramos_detalle[5]['potencia_hp'] = 0.0
    tramos_detalle[5]['num_estaciones'] = 1
    tramos_detalle[5]['tipo'] = 'valvula_estrangulamiento'
    
    # Tramo 6
    tramos_detalle[6]['z'] = 0.0
    tramos_detalle[6]['carga_total_estacion'] = 1.33
    tramos_detalle[6]['carga_total'] = 2.66
    tramos_detalle[6]['potencia_kw'] = 0.0
    tramos_detalle[6]['potencia_hp'] = 0.0
    tramos_detalle[6]['num_estaciones'] = 1
    tramos_detalle[6]['tipo'] = 'valvula_estrangulamiento'
    
    # Tramo 7
    tramos_detalle[7]['z'] = 0.0
    tramos_detalle[7]['carga_total'] = 1.38
    tramos_detalle[7]['potencia_kw'] = 0.0
    tramos_detalle[7]['potencia_hp'] = 0.0
    tramos_detalle[7]['num_estaciones'] = 1
    tramos_detalle[7]['tipo'] = 'valvula_estrangulamiento'
    
    # Tramo 8
    tramos_detalle[8] = {
        'pendiente': 0,
        'densidad': 998,
        'caudal': 0.025,
        'viscosidad': 0.001,
        'longitud_tuberia': 1911.52,
        'rugosidad': 0.000046,
        'diametro': 0.1541,
        'area': 0.01865,
        'velocidad': 1.34,
        'carga_cinetica': 0.0916,
        'reynolds': 206147.48,
        'f_colebrook': 0.017649,
        'f_haaland': 0.017438,
        'perdidas_darcy_crane': 2.2144,
        'perdidas_darcy_haaland': 2.1879,
        'z': 100.0,
        'carga_total': 120.57,
        'potencia_kw': 36.89,
        'potencia_hp': 49.47,
        'num_estaciones': 1,
        'tipo': 'bomba',
        'accesorios': extraer_accesorios_tramo_8(filas),
    }
    
    return {
        'perfil_terreno': perfil,
        'parametros': parametros,
        'resumen_tramos': resumen,
        'tramo_8_distancias': tramo8_dist,
        'tramos_detalle': tramos_detalle,
    }
