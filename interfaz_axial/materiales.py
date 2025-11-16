# materiales.py
DEFAULT_FACTOR_SEGURIDAD = 3.0
ESBELTEZ_CRITERIO = 12.0  # si lambda > 12 se evalúa Euler

# Base de datos de materiales
# f_c en MPa, E en GPa
MATERIALES = {
    "concreto_25": {"nombre": "Concreto f'c=25 MPa", "f_c": 25.0, "E_GPa": 25.0},
    "concreto_20": {"nombre": "Concreto f'c=20 MPa", "f_c": 20.0, "E_GPa": 25.0},
    "acero_250":  {"nombre": "Acero S250 (σy≈250 MPa)", "f_c": 250.0, "E_GPa": 200.0},
}
