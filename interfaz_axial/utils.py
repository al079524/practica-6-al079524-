# utils.py
import math

def validar_numero(valor, nombre_campo, positive=True):
    """Valida que un valor sea numérico y opcionalmente positivo."""
    try:
        val = float(valor)
    except Exception:
        raise ValueError(f"'{nombre_campo}' debe ser un número válido (entrada: {valor})")

    if positive and val <= 0:
        raise ValueError(f"'{nombre_campo}' debe ser mayor que cero (entrada: {valor})")

    return val


def parsear_seccion_raw(seccion_raw):
    """
    Interpreta:
    - área simple
    - o [área, radio de giro]
    Si no se da r, se aproxima usando r = sqrt(area/12).
    """
    if isinstance(seccion_raw, (list, tuple)) and len(seccion_raw) >= 1:
        area = validar_numero(seccion_raw[0], "sección.area", True)

        if len(seccion_raw) >= 2 and seccion_raw[1] is not None:
            r = validar_numero(seccion_raw[1], "sección.radio_de_giro", True)
        else:
            r = math.sqrt(area / 12.0)

        return area, r

    # solo área
    area = validar_numero(seccion_raw, "sección(area)", True)
    r = math.sqrt(area / 12.0)
    return area, r
