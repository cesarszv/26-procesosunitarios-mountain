"""
hidraulica.py — Motor de cálculos hidráulicos.

Implementa todas las fórmulas de mecánica de fluidos:
Reynolds, Colebrook-White, Haaland, Darcy-Weisbach,
pérdidas menores y potencia de bombas.
"""

import numpy as np
from scipy.optimize import fsolve

# Constante gravitacional
g = 9.81  # m/s²


def area_seccion(D: float) -> float:
    """Área de la sección transversal circular. A = π·D²/4"""
    return np.pi * D**2 / 4


def velocidad(Q: float, A: float) -> float:
    """Velocidad del flujo. v = Q/A"""
    return Q / A


def carga_cinetica(v: float) -> float:
    """Carga cinética (cabeza de velocidad). hv = v²/(2g)"""
    return v**2 / (2 * g)


def reynolds(rho: float, v: float, D: float, mu: float) -> float:
    """
    Número de Reynolds.
    Re = ρ·v·D / μ
    
    Parámetros:
        rho: densidad del fluido (kg/m³)
        v: velocidad del flujo (m/s)
        D: diámetro interno de la tubería (m)
        mu: viscosidad dinámica (Pa·s)
    """
    return rho * v * D / mu


def f_haaland(Re: float, epsilon: float, D: float) -> float:
    """
    Factor de fricción por la correlación de Haaland (explícita).
    
    1/√f = -1.8·log₁₀[(ε/D / 3.7)^1.11 + 6.9/Re]
    """
    if Re <= 0:
        return 0.0
    termino = (epsilon / D / 3.7)**1.11 + 6.9 / Re
    inv_sqrt_f = -1.8 * np.log10(termino)
    return 1.0 / inv_sqrt_f**2


def f_colebrook(Re: float, epsilon: float, D: float) -> float:
    """
    Factor de fricción por la ecuación de Colebrook-White (implícita).
    
    1/√f = -2·log₁₀(ε/D / 3.7 + 2.51/(Re·√f))
    
    Resuelve iterativamente usando scipy.optimize.fsolve,
    con la solución de Haaland como semilla inicial.
    """
    if Re <= 0:
        return 0.0
    
    # Semilla: Haaland
    f0 = f_haaland(Re, epsilon, D)
    
    def ecuacion(f):
        if f <= 0:
            return 1.0
        return (1.0 / np.sqrt(f) + 
                2.0 * np.log10(epsilon / D / 3.7 + 2.51 / (Re * np.sqrt(f))))
    
    sol = fsolve(ecuacion, f0, full_output=False)
    return float(sol[0])


def f_swamee_jain(Re: float, epsilon: float, D: float) -> float:
    """
    Factor de fricción por la ecuación de Swamee-Jain (explícita).
    
    f = 0.25 / [log₁₀(ε/(3.7·D) + 5.74/Re^0.9)]²
    """
    if Re <= 0:
        return 0.0
    termino = epsilon / (3.7 * D) + 5.74 / Re**0.9
    return 0.25 / (np.log10(termino))**2


def perdidas_darcy(f: float, L: float, D: float, v: float) -> float:
    """
    Pérdidas por fricción (Darcy-Weisbach).
    
    hf = f · (L/D) · v²/(2g)
    
    Parámetros:
        f: factor de fricción (adimensional)
        L: longitud de la tubería (m)
        D: diámetro interno (m)
        v: velocidad del flujo (m/s)
    """
    return f * (L / D) * v**2 / (2 * g)


def perdidas_menores(K_total: float, v: float) -> float:
    """
    Pérdidas menores por accesorios.
    
    hm = ΣK · v²/(2g)
    
    Parámetros:
        K_total: suma de coeficientes K de todos los accesorios
        v: velocidad del flujo (m/s)
    """
    return K_total * v**2 / (2 * g)


def carga_total(z: float, hf: float, hm: float) -> float:
    """
    Carga total del sistema.
    
    H = z + hf + hm
    
    Parámetros:
        z: diferencia de elevación (m)
        hf: pérdidas por fricción (m)
        hm: pérdidas menores (m)
    """
    return z + hf + hm


def potencia_bomba(rho: float, Q: float, H: float) -> float:
    """
    Potencia de la bomba hidráulica.
    
    P = ρ · g · Q · H  (en Watts)
    
    Retorna potencia en kW.
    """
    return rho * g * Q * H / 1000.0


def kw_a_hp(P_kw: float) -> float:
    """Convierte potencia de kW a HP."""
    return P_kw / 0.7457


def calcular_tramo(
    Q: float, D: float, L: float, z: float,
    rho: float = 998.0, mu: float = 0.001,
    epsilon: float = 0.000046,
    K_total: float = 0.0,
    num_estaciones: int = 1,
    es_bajada: bool = False,
) -> dict:
    """
    Calcula todos los parámetros hidráulicos para un tramo de tubería.
    
    Parámetros:
        Q: caudal (m³/s)
        D: diámetro interno (m)
        L: longitud de tubería (m)
        z: diferencia de elevación (m) — positiva subida, negativa bajada
        rho: densidad del fluido (kg/m³)
        mu: viscosidad dinámica (Pa·s)
        epsilon: rugosidad absoluta (m)
        K_total: suma de coeficientes K de accesorios
        num_estaciones: número de estaciones de bombeo en el tramo
        es_bajada: si True, el tramo es descendente (usa válvula en vez de bomba)
    
    Retorna dict con todos los valores calculados.
    """
    A = area_seccion(D)
    v = velocidad(Q, A)
    hv = carga_cinetica(v)
    Re = reynolds(rho, v, D, mu)
    
    f_col = f_colebrook(Re, epsilon, D)
    f_haa = f_haaland(Re, epsilon, D)
    f_swa = f_swamee_jain(Re, epsilon, D)
    
    # Longitud por estación
    L_estacion = L / num_estaciones if num_estaciones > 0 else L
    
    # Pérdidas por fricción (por estación)
    hf_crane = perdidas_darcy(f_col, L_estacion, D, v)
    hf_haaland = perdidas_darcy(f_haa, L_estacion, D, v)
    
    # Pérdidas menores
    hm = perdidas_menores(K_total, v)
    
    # Elevación por estación
    z_estacion = z / num_estaciones if num_estaciones > 0 else z
    
    # Carga total por estación
    H_estacion = carga_total(abs(z_estacion), hf_crane, hm)
    
    # Carga total del tramo
    H_total = H_estacion * num_estaciones
    
    # Potencia
    if es_bajada:
        P_kw = 0.0
        P_hp = 0.0
    else:
        P_kw = potencia_bomba(rho, Q, H_estacion)
        P_hp = kw_a_hp(P_kw)
    
    return {
        'area': A,
        'velocidad': v,
        'carga_cinetica': hv,
        'reynolds': Re,
        'f_colebrook': f_col,
        'f_haaland': f_haa,
        'f_swamee_jain': f_swa,
        'longitud_estacion': L_estacion,
        'perdidas_friccion_colebrook': hf_crane,
        'perdidas_friccion_haaland': hf_haaland,
        'perdidas_menores': hm,
        'z_estacion': z_estacion,
        'carga_estacion': H_estacion,
        'carga_total': H_total,
        'potencia_kw': P_kw,
        'potencia_hp': P_hp,
        'num_estaciones': num_estaciones,
        'es_bajada': es_bajada,
    }


def calcular_sistema_completo(
    Q: float = 0.025,
    D: float = 0.1541,
    rho: float = 998.0,
    mu: float = 0.001,
    epsilon: float = 0.000046,
) -> dict:
    """
    Recalcula todo el sistema hidráulico con los parámetros dados.
    
    Usa las geometrías fijas de los 8 tramos (distancias, alturas, accesorios)
    pero permite cambiar los parámetros del fluido y la tubería.
    
    Retorna dict con resultados para cada tramo.
    """
    from core.tramos import obtener_definicion_tramos
    
    definiciones = obtener_definicion_tramos()
    resultados = {}
    
    for num_tramo, defn in definiciones.items():
        resultado = calcular_tramo(
            Q=Q, D=D,
            L=defn['longitud_tuberia'],
            z=defn['z'],
            rho=rho, mu=mu, epsilon=epsilon,
            K_total=defn['K_total'],
            num_estaciones=defn['num_estaciones'],
            es_bajada=defn['es_bajada'],
        )
        resultado['distancia'] = defn['distancia']
        resultado['altura'] = defn['altura']
        resultado['pendiente'] = defn['pendiente']
        resultado['longitud_tuberia'] = defn['longitud_tuberia']
        resultado['tipo'] = defn['tipo']
        resultado['accesorios'] = defn['accesorios']
        resultado['notas'] = defn.get('notas', '')
        resultados[num_tramo] = resultado
    
    return resultados
