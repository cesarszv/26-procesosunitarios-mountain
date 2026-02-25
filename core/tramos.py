"""
tramos.py — Definición de los 8 tramos del sistema hidráulico.

Cada tramo contiene su geometría fija (distancia, altura, pendiente),
los accesorios instalados (codos, válvulas, entradas/salidas), y
las decisiones de ingeniería (número de estaciones, tipo de control).
"""


def obtener_definicion_tramos() -> dict:
    """
    Retorna la definición geométrica y de accesorios de los 8 tramos.
    
    Los datos provienen del CSV original y del mapa topográfico.
    La geometría es fija; lo que cambia al interactuar son Q, D, ρ, μ, ε.
    """
    tramos = {}

    # ==============================
    # TRAMO 1: Río → primera estación (subida)
    # ==============================
    tramos[1] = {
        'distancia': 182.53,
        'altura': 100.0,
        'pendiente': 28.72,
        'longitud_tuberia': 211.13,
        'z': 100.0,
        'num_estaciones': 1,
        'es_bajada': False,
        'tipo': 'bomba',
        'accesorios': [
            {'nombre': 'Entrada al río (proyectada)', 'cantidad': 1, 'K': 0.5},
            {'nombre': 'Codos de 30°', 'cantidad': 2, 'K': 0.12},
            {'nombre': 'Válvula de retención columpio', 'cantidad': 0, 'K': 0.0},
            {'nombre': 'Válvula de compuerta', 'cantidad': 0, 'K': 0.0},
            {'nombre': 'Salida a tanque receptor', 'cantidad': 1, 'K': 1.0},
        ],
        'K_total': 1.62,
        'notas': 'Captación desde el río, subida inicial de 100 m.',
    }

    # ==============================
    # TRAMO 2: Subida fuerte — 2 estaciones de bombeo
    # ==============================
    tramos[2] = {
        'distancia': 112.39,
        'altura': 200.0,
        'pendiente': 60.67,
        'longitud_tuberia': 235.42,
        'z': 200.0,
        'num_estaciones': 2,
        'es_bajada': False,
        'tipo': 'bomba',
        'accesorios': [
            {'nombre': 'Succión de tanque previo', 'cantidad': 1, 'K': 0.5},
            {'nombre': 'Codos de 60°', 'cantidad': 2, 'K': 0.375},
            {'nombre': 'Válvula de retención columpio', 'cantidad': 0, 'K': 1.5},
            {'nombre': 'Válvula de compuerta', 'cantidad': 0, 'K': 0.12},
            {'nombre': 'Salida a tanque receptor', 'cantidad': 1, 'K': 1.0},
        ],
        'K_total': 3.87,
        'notas': '2 estaciones de bombeo. Pendiente pronunciada (60.67°).',
    }

    # ==============================
    # TRAMO 3: Subida fuerte — 2 estaciones de bombeo
    # ==============================
    tramos[3] = {
        'distancia': 163.87,
        'altura': 200.0,
        'pendiente': 50.67,
        'longitud_tuberia': 264.56,
        'z': 200.0,
        'num_estaciones': 2,
        'es_bajada': False,
        'tipo': 'bomba',
        'accesorios': [
            {'nombre': 'Salida de tanque previo', 'cantidad': 1, 'K': 0.5},
            {'nombre': 'Codos de 51°', 'cantidad': 2, 'K': 0.28},
            {'nombre': 'Válvula de retención columpio', 'cantidad': 0, 'K': 1.5},
            {'nombre': 'Válvula de compuerta', 'cantidad': 0, 'K': 0.12},
            {'nombre': 'Salida a tanque receptor', 'cantidad': 1, 'K': 1.0},
        ],
        'K_total': 3.68,
        'notas': '2 estaciones de bombeo. Cima de la montaña.',
    }

    # ==============================
    # TRAMO 4: Plano — bomba pequeña
    # ==============================
    tramos[4] = {
        'distancia': 251.55,
        'altura': 0.0,
        'pendiente': 0.0,
        'longitud_tuberia': 254.55,
        'z': 0.0,
        'num_estaciones': 1,
        'es_bajada': False,
        'tipo': 'bomba',
        'accesorios': [
            {'nombre': 'Salida de tanque previo', 'cantidad': 1, 'K': 0.5},
            {'nombre': 'Codos de 90° (arreglo al suelo)', 'cantidad': 2, 'K': 0.45},
            {'nombre': 'Válvula de retención columpio', 'cantidad': 0, 'K': 1.5},
            {'nombre': 'Válvula de compuerta', 'cantidad': 0, 'K': 0.12},
            {'nombre': 'Salida a tanque receptor', 'cantidad': 1, 'K': 1.0},
        ],
        'K_total': 4.02,
        'notas': 'Tramo plano. Bomba de 2 kW para evitar sobrecarga.',
    }

    # ==============================
    # TRAMO 5: Bajada — válvula de estrangulamiento
    # ==============================
    tramos[5] = {
        'distancia': 129.05,
        'altura': -200.0,
        'pendiente': -57.17,
        'longitud_tuberia': 235.02,
        'z': 0.0,  # No se bombea, la gravedad hace el trabajo
        'num_estaciones': 1,
        'es_bajada': True,
        'tipo': 'válvula de estrangulamiento',
        'accesorios': [
            {'nombre': 'Salida de tanque previo', 'cantidad': 1, 'K': 0.5},
            {'nombre': 'Codos de ángulo dado', 'cantidad': 2, 'K': 0.35},
            {'nombre': 'Válvula de compuerta', 'cantidad': 0, 'K': 0.12},
            {'nombre': 'Salida a tanque receptor', 'cantidad': 1, 'K': 1.0},
        ],
        'K_total': 2.31,
        'notas': 'Bajada gravitacional. Válvula de estrangulamiento controla velocidad a 1.34 m/s.',
    }

    # ==============================
    # TRAMO 6: Bajada — válvula de estrangulamiento
    # ==============================
    tramos[6] = {
        'distancia': 71.33,
        'altura': -200.0,
        'pendiente': -70.37,
        'longitud_tuberia': 209.34,
        'z': 0.0,
        'num_estaciones': 1,
        'es_bajada': True,
        'tipo': 'válvula de estrangulamiento',
        'accesorios': [
            {'nombre': 'Salida de tanque previo', 'cantidad': 1, 'K': 0.5},
            {'nombre': 'Codos de ángulo dado', 'cantidad': 2, 'K': 0.53},
            {'nombre': 'Válvula de compuerta', 'cantidad': 0, 'K': 0.12},
            {'nombre': 'Salida a tanque receptor', 'cantidad': 1, 'K': 1.0},
        ],
        'K_total': 2.68,
        'K_valvula_estrangulamiento': 1077.42,
        'notas': 'Bajada pronunciada (70.37°). K de estrangulamiento = 1077.42.',
    }

    # ==============================
    # TRAMO 7: Bajada final
    # ==============================
    tramos[7] = {
        'distancia': 57.60,
        'altura': -100.0,
        'pendiente': -60.06,
        'longitud_tuberia': 112.40,
        'z': 0.0,
        'num_estaciones': 1,
        'es_bajada': True,
        'tipo': 'válvula de estrangulamiento',
        'accesorios': [
            {'nombre': 'Salida de tanque previo', 'cantidad': 1, 'K': 0.5},
            {'nombre': 'Codos de 60°', 'cantidad': 2, 'K': 0.38},
            {'nombre': 'Válvula de compuerta', 'cantidad': 0, 'K': 0.12},
            {'nombre': 'Salida a tanque receptor', 'cantidad': 1, 'K': 1.0},
        ],
        'K_total': 2.37,
        'K_valvula_estrangulamiento': 1076.84,
        'notas': 'Bajada final a zona plana. K de estrangulamiento = 1076.84.',
    }

    # ==============================
    # TRAMO 8: Subterráneo — hacia la empresa
    # ==============================
    tramos[8] = {
        'distancia': 1837.50,
        'altura': 100.0,
        'pendiente': 0.0,
        'longitud_tuberia': 1911.52,
        'z': 100.0,
        'num_estaciones': 1,
        'es_bajada': False,
        'tipo': 'bomba',
        'accesorios': [
            {'nombre': 'Entrada al tanque', 'cantidad': 1, 'K': 0.5},
            {'nombre': 'Codos de 90°', 'cantidad': 4, 'K': 0.45},
            {'nombre': 'Codos de 60°', 'cantidad': 2, 'K': 0.375},
            {'nombre': 'Válvula de compuerta', 'cantidad': 1, 'K': 0.12},
            {'nombre': 'Válvula de retención', 'cantidad': 1, 'K': 1.5},
            {'nombre': 'Salida a tanque en empresa', 'cantidad': 1, 'K': 1.0},
        ],
        'K_total': 5.67,
        'notas': 'Tramo subterráneo. Cruza carretera (700 m). 4 codos de 90° + 2 de 60°.',
        'sub_segmentos': [
            {'nombre': 'Distancia previa a carretera', 'distancia': 250.0, 'altura': 0},
            {'nombre': 'Bajada', 'distancia': 0.0, 'altura': -10},
            {'nombre': 'Tubería subterránea', 'distancia': 312.5, 'altura': -10},
            {'nombre': 'Cambio de dirección', 'distancia': 25.0, 'altura': -10},
            {'nombre': 'Distancia subterránea', 'distancia': 1187.5, 'altura': -10},
            {'nombre': 'Subida a empresa', 'distancia': 62.5, 'altura': 100},
            {'nombre': 'Tramo de subida', 'distancia': 126.52, 'altura': None},
        ],
    }

    return tramos


def obtener_elevaciones_acumuladas() -> list[dict]:
    """
    Calcula las elevaciones y distancias acumuladas en los puntos
    de unión entre tramos (para el perfil topográfico).
    
    Retorna lista de puntos: [{distancia_acum, elevacion, tramo}]
    """
    tramos = obtener_definicion_tramos()
    
    # Punto de inicio: río (elevación 0, distancia 87.5 m desde la referencia)
    puntos = [{'distancia_acum': 0.0, 'elevacion': 0.0, 'tramo': 0, 'nombre': 'Río'}]
    
    dist_acum = 0.0
    elev_acum = 0.0
    
    for i in range(1, 8):
        t = tramos[i]
        dist_acum += t['distancia']
        elev_acum += t['altura']
        puntos.append({
            'distancia_acum': dist_acum,
            'elevacion': elev_acum,
            'tramo': i,
            'nombre': f'Fin Tramo {i}',
        })
    
    # Tramo 8 (subterráneo)
    for seg in tramos[8]['sub_segmentos']:
        if seg['altura'] is not None:
            dist_acum += seg['distancia']
            elev_acum += seg['altura']
            puntos.append({
                'distancia_acum': dist_acum,
                'elevacion': elev_acum,
                'tramo': 8,
                'nombre': seg['nombre'],
            })
    
    return puntos
