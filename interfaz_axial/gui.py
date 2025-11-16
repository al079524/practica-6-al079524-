# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from calculos import calcular_volumenes_totales
from pruebas import pruebas_unitarias
from materiales import MATERIALES

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

        mat_text = "Materiales: " + ", ".join(MATERIALES.keys())
        ttk.Label(frame_in, text=mat_text).grid(row=5, column=0, columnspan=2, pady=4)

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
