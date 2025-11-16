# calculos.py
import math
from utils import validar_numero, parsear_seccion_raw
from materiales import MATERIALES, DEFAULT_FACTOR_SEGURIDAD, ESBELTEZ_CRITERIO


def calcular_carga_material_admisible(area_m2, f_c_MPa, factor_seguridad=DEFAULT_FACTOR_SEGURIDAD):
    """Carga admisible según resistencia simple."""
    area = validar_numero(area_m2, "area_m2")
    f_c = validar_numero(f_c_MPa, "f_c_MPa")
    fs = validar_numero(factor_seguridad, "factor_seguridad")

    return area * f_c * 1000.0 / fs  # kN


def calcular_euler_admisible(area_m2, r_m, altura_m, E_GPa, K_factor=0.5, factor_seguridad=DEFAULT_FACTOR_SEGURIDAD):
    """Carga crítica de Euler convertida a admisible."""
    A = validar_numero(area_m2, "area_m2")
    r = validar_numero(r_m, "r_m")
    L = validar_numero(altura_m, "altura_m")
    E_GPa = validar_numero(E_GPa, "E_GPa")
    K = validar_numero(K_factor, "K_factor")
    fs = validar_numero(factor_seguridad, "factor_seguridad")

    I = A * (r ** 2)
    Le = K * L
    E_Pa = E_GPa * 1e9

    Pcr_N = (math.pi ** 2) * E_Pa * I / (Le ** 2)
    return (Pcr_N / 1000.0) / fs  # kN


def calcular_carga_admisible(columna, materiales_dic=MATERIALES, factor_seguridad=DEFAULT_FACTOR_SEGURIDAD, K_factor=0.5):
    """
    columna = [id, altura_m, seccion(area o [area,r]), material_key, carga_aplicada_kN]
    Devuelve un diccionario con resultados completos.
    """
    id_col = columna[0]
    altura_m = validar_numero(columna[1], f"altura {id_col}")
    area_m2, r_m = parsear_seccion_raw(columna[2])
    material_key = columna[3]
    carga_aplicada_kN = validar_numero(columna[4], f"carga_aplicada {id_col}")

    if material_key not in materiales_dic:
        raise ValueError(f"Material '{material_key}' no registrado.")

    mat = materiales_dic[material_key]
    f_c_MPa = mat["f_c"]
    E_GPa = mat["E_GPa"]

    carga_mat = calcular_carga_material_admisible(area_m2, f_c_MPa, factor_seguridad)

    Le = K_factor * altura_m
    lambda_rel = Le / r_m

    euler_adm = None
    carga_final = carga_mat
    control = "material"

    if lambda_rel > ESBELTEZ_CRITERIO:
        euler_adm = calcular_euler_admisible(area_m2, r_m, altura_m, E_GPa, K_factor, factor_seguridad)
        carga_final = min(carga_mat, euler_adm)
        control = "Euler" if euler_adm < carga_mat else "material"

    delta = carga_aplicada_kN - carga_final

    veredicto = (
        "falla por sobrecarga" if delta > 0
        else "margen disponible" if delta < 0
        else "equilibrio"
    )

    return {
        "id": id_col,
        "altura_m": altura_m,
        "area_m2": area_m2,
        "r_m": r_m,
        "material": material_key,
        "f_c_MPa": f_c_MPa,
        "E_GPa": E_GPa,
        "carga_aplicada_kN": carga_aplicada_kN,
        "carga_adm_material_kN": carga_mat,
        "euler_adm_kN": euler_adm,
        "carga_adm_final_kN": carga_final,
        "lambda": lambda_rel,
        "control": control,
        "delta_kN": delta,
        "veredicto": veredicto,
    }


def calcular_volumenes_totales(matriz_columnas, materiales_dic=MATERIALES, factor_seguridad=DEFAULT_FACTOR_SEGURIDAD, K_factor=0.5):
    resultados = []
    total_exceso = 0.0
    total_relleno = 0.0

    for col in matriz_columnas:
        try:
            res = calcular_carga_admisible(col, materiales_dic, factor_seguridad, K_factor)
            resultados.append(res)

            if res["delta_kN"] > 0:
                total_exceso += res["delta_kN"]
            else:
                total_relleno += abs(res["delta_kN"])

        except Exception as e:
            resultados.append({"id": col[0], "error": str(e)})

    return resultados, {"total_exceso_kN": total_exceso, "total_relleno_kN": total_relleno}
