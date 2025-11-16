#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Programa completo para calcular la carga axial admisible de columnas.
Incluye:
- Datos de materiales
- Validación de entradas
- Cálculo por resistencia del material
- Cálculo de Euler
- Análisis de esbeltez
- Interfaz gráfica (Tkinter)
- Pruebas unitarias
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# 1. MATERIALES Y CONSTANTES
# ============================================================

DEFAULT_FACTOR_SEGURIDAD = 3.0
ESBELTEZ_CRITERIO = 12.0  # Si lambda > 12, se evalúa Euler

MATERIALES = {
    "concreto_25": {"nombre": "Concreto f'c=25 MPa", "f_c": 25.0, "E_GPa": 25.0},
    "concreto_20": {"nombre": "Concreto f'c=20 MPa", "f_c": 20.0, "E_GPa": 25.0},
    "acero_250": {"nombre": "Acero S250", "f_c": 250.0, "E_GPa": 200.0},
}


# ============================================================
# 2. FUNCIONES AUXILIARES (VALIDACIONES Y PARSEO)
# ============================================================

def validar_numero(valor, nombre_campo, positive=True):
    try:
        val = float(valor)
    except Exception:
        raise ValueError(f"'{nombre_campo}' debe ser un número válido (recibido: {valor})")

    if positive and val <= 0:
        raise ValueError(f"'{nombre_campo}' debe ser mayor que cero (recibido: {valor})")

    return val


def parsear_seccion_raw(seccion_raw):
    """Interpreta: área sola o lista [área, r]. Si no hay r, se calcula r = sqrt(area/12)."""

    if isinstance(seccion_raw, (list, tuple)) and len(seccion_raw) >= 1:
        area = validar_numero(seccion_raw[0], "sección.area", True)

        if len(seccion_raw) >= 2 and seccion_raw[1] is not None:
            r = validar_numero(seccion_raw[1], "sección.radio_de_giro", True)
        else:
            r = math.sqrt(area / 12.0)

        return area, r

    area = validar_numero(seccion_raw, "sección(area)", True)
    r = math.sqrt(area / 12.0)
    return area, r


# ============================================================
# 3. FUNCIONES DE CÁLCULO
# ============================================================

def calcular_carga_material_admisible(area_m2, f_c_MPa, factor_seguridad=DEFAULT_FACTOR_SEGURIDAD):
    area = validar_numero(area_m2, "area_m2")
    f_c = validar_numero(f_c_MPa, "f_c_MPa")
    fs = validar_numero(factor_seguridad, "factor_seguridad")
    return area * f_c * 1000.0 / fs  # kN


def calcular_euler_admisible(area_m2, r_m, altura_m, E_GPa, K_factor=0.5, factor_seguridad=DEFAULT_FACTOR_SEGURIDAD):
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


# ============================================================
# 4. PRUEBAS UNITARIAS
# ============================================================

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
        evaluacion.append((r["id"], r.get("veredicto", "ERROR")))

    return {"resultados": resultados, "resumen": resumen, "evaluacion": evaluacion}


# ============================================================
# 5. INTERFAZ GRÁFICA (Tkinter)
# ============================================================

class ColumnApp:
    def __init__(self, root):
        root.title("Cálculo de carga axial admisible - Columnas")
        root.geometry("1000x600")

        self.matriz_columnas = []
        self.factor_seguridad = tk.DoubleVar(value=3.0)
        self.K_factor = tk.DoubleVar(value=0.5)

        frame_in = ttk.LabelFrame(root, text="Ingresar columna")
        frame_in.pack(fill="x", padx=8, pady=6)

        labels = ["ID", "Altura (m)", "Sección (m²) o [area,r]", "Material (clave)", "Carga aplicada (kN)"]
        self.entries = []

        for i, lab in enumerate(labels):
            ttk.Label(frame_in, text=lab).grid(row=i, column=0, sticky="w")
            ent = ttk.Entry(frame_in, width=40)
            ent.grid(row=i, column=1)
            self.entries.append(ent)

        ttk.Label(frame_in, text="Materiales: " + ", ".join(MATERIALES.keys())).grid(row=5, column=0, columnspan=2, pady=4)

        ttk.Label(frame_in, text="Factor seguridad:").grid(row=0, column=2)
        ttk.Spinbox(frame_in, from_=1.1, to=10.0, increment=0.1, textvariable=self.factor_seguridad).grid(row=0, column=3)

        ttk.Label(frame_in, text="K:").grid(row=1, column=2)
        ttk.Spinbox(frame_in, from_=0.2, to=2.0, increment=0.1, textvariable=self.K_factor).grid(row=1, column=3)

        ttk.Button(frame_in, text="Agregar", command=self.agregar_columna).grid(row=6, column=1, pady=6)
        ttk.Button(frame_in, text="Limpiar", command=self.limpiar_campos).grid(row=6, column=2, pady=6)

        frame_list = ttk.LabelFrame(root, text="Columnas ingresadas")
        frame_list.pack(fill="both", expand=True, padx=8, pady=6)

        cols = ("id", "altura", "seccion", "material", "carga")
        self.tree = ttk.Treeview(frame_list, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)

        frame_buttons = ttk.Frame(root)
        frame_buttons.pack(fill="x")

        ttk.Button(frame_buttons, text="Calcular", command=self.calcular_gui).pack(side="left", padx=6)
        ttk.Button(frame_buttons, text="Pruebas", command=self.ejecutar_pruebas_gui).pack(side="left", padx=6)
        ttk.Button(frame_buttons, text="Eliminar", command=self.eliminar_seleccion).pack(side="left", padx=6)

        frame_res = ttk.LabelFrame(root, text="Resultados")
        frame_res.pack(fill="both", expand=True, padx=8, pady=6)

        cols_res = ("id", "c_aplicada", "c_adm", "lambda", "delta", "veredicto")
        self.tree_res = ttk.Treeview(frame_res, columns=cols_res, show="headings")
        for c in cols_res:
            self.tree_res.heading(c, text=c)
        self.tree_res.pack(fill="both", expand=True)

    def limpiar_campos(self):
        for e in self.entries:
            e.delete(0, tk.END)

    def agregar_columna(self):
        try:
            idv = self.entries[0].get().strip()
            altura = self.entries[1].get().strip()
            seccion = self.entries[2].get().strip()
            material = self.entries[3].get().strip()
            carga = self.entries[4].get().strip()

            if not idv:
                messagebox.showwarning("Error", "El ID no puede estar vacío.")
                return

            if seccion.startswith("[") or "," in seccion:
                try:
                    s = seccion.replace(" ", "")
                    if s.startswith("[") and s.endswith("]"):
                        s = s[1:-1]
                    parts = s.split(",")
                    vals = [float(p) for p in parts]
                    seccion_parsed = vals
                except:
                    seccion_parsed = seccion
            else:
                seccion_parsed = seccion

            nueva = [idv, altura, seccion_parsed, material, carga]
            self.matriz_columnas.append(nueva)

            self.tree.insert("", tk.END, values=(idv, altura, seccion_parsed, material, carga))
            self.limpiar_campos()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_seleccion(self):
        sel = self.tree.selection()
        if sel:
            val = self.tree.item(sel[0], "values")
            idb = val[0]
            self.matriz_columnas = [c for c in self.matriz_columnas if str(c[0]) != str(idb)]
            self.tree.delete(sel[0])

    def calcular_gui(self):
        for i in self.tree_res.get_children():
            self.tree_res.delete(i)

        try:
            fs = float(self.factor_seguridad.get())
            K = float(self.K_factor.get())
            resultados, resumen = calcular_volumenes_totales(self.matriz_columnas, MATERIALES, fs, K)

            for r in resultados:
                if "error" in r:
                    self.tree_res.insert("", tk.END, values=(r["id"], "Error", r["error"], "-", "-", "ERROR"))
                else:
                    self.tree_res.insert("", tk.END, values=(
                        r["id"],
                        f"{r['carga_aplicada_kN']:.3f}",
                        f"{r['carga_adm_final_kN']:.3f}",
                        f"{r['lambda']:.3f}",
                        f"{r['delta_kN']:.3f}",
                        r["veredicto"],
                    ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ejecutar_pruebas_gui(self):
        res = pruebas_unitarias()
        messagebox.showinfo("Pruebas", str(res))


# ============================================================
# 6. PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = ColumnApp(root)
    root.mainloop()
