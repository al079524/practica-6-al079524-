# pruebas.py
from calculos import calcular_volumenes_totales
from materiales import MATERIALES, DEFAULT_FACTOR_SEGURIDAD

def pruebas_unitarias():
    fs = DEFAULT_FACTOR_SEGURIDAD
    K = 0.5

    col1 = ["C1", 3.0, 0.04, "concreto_25", 200.0]
    col2 = ["C2", 6.0, [0.02, 0.01], "concreto_25", 50.0]
    col3 = ["C3", 3.0, 0.02, "acero_250", 150.0]

    casos = [col1, col2, col3]
    resultados, resumen = calcular_volumenes_totales(casos, MATERIALES, fs, K)

    evaluacion = []
    for r in resultados:
        if "error" in r:
            evaluacion.append((r["id"], "ERROR"))
        else:
            evaluacion.append((r["id"], r["veredicto"]))

    return {
        "resultados": resultados,
        "resumen": resumen,
        "evaluacion": evaluacion,
    }
