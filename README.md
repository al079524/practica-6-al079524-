# practica-6-al079524-
modelado de problema aplicado a la ingeniería civil
🏗️ Cálculo de Carga Axial Admisible en Columnas

Este proyecto es una aplicación desarrollada en Python que calcula la carga axial admisible en columnas sometidas a compresión.
Incluye un modelo matemático completo, funciones de análisis estructural y una interfaz gráfica (Tkinter) que facilita su uso sin necesidad de conocimientos avanzados de programación.

📌 ¿Qué hace este proyecto?
✔️ 1. Recibe los datos de una columna

El programa permite ingresar:

ID de la columna

Altura (m)

Área o área + radio de giro

Material (concreto o acero)

Carga aplicada (kN)

Estos datos se procesan para generar parámetros estructurales.

✔️ 2. Calcula la carga admisible del material

Usa la fórmula fundamental de compresión:

𝑃
adm
=
𝐴
⋅
𝑓
𝑐
⋅
1000
𝐹
𝑆
P
adm
	​

=
FS
A⋅f
c
	​

⋅1000
	​


donde

A = área (m²)

fₐ = resistencia del material (MPa)

FS = factor de seguridad

Este cálculo aplica cuando la columna no es esbelta.

✔️ 3. Evalúa la esbeltez

El sistema calcula la relación de esbeltez:

𝜆
=
𝐾
𝐿
𝑟
λ=
r
KL
	​


λ ≤ 12 → la columna se considera corta

λ > 12 → la columna es esbelta y se evalúa pandeo

✔️ 4. Calcula el pandeo por la fórmula de Euler

Si la columna es esbelta:

𝑃
𝑐
𝑟
=
𝜋
2
𝐸
𝐼
(
𝐾
𝐿
)
2
P
cr
	​

=
(KL)
2
π
2
EI
	​


Luego se obtiene:

𝑃
adm,Euler
=
𝑃
𝑐
𝑟
𝐹
𝑆
P
adm,Euler
	​

=
FS
P
cr
	​

	​


El programa selecciona automáticamente la carga admisible más crítica entre:

Resistencia del material

Pandeo por Euler

✔️ 5. Determina si la columna es segura

Se evalúa:

Δ
=
𝑃
aplicada
−
𝑃
admisible
Δ=P
aplicada
	​

−P
admisible
	​


El proyecto indica:

Falla por sobrecarga

Margen disponible

Equilibrio aproximado

✔️ 6. Permite analizar múltiples columnas

El programa puede recibir una matriz completa de columnas, calcular cada una y generar:

Total de carga excedida (fallas)

Total de carga sobrante (margen)

Tabla de resultados por columna

✔️ 7. Incluye una interfaz gráfica (GUI)

La interfaz permite:

Agregar columnas

Seleccionar materiales

Ajustar parámetros (FS y K)

Ver todas las columnas ingresadas

Ejecutar los cálculos

Mostrar resultados en tablas

Ver informes detallados

Ejecutar pruebas automáticas

Todo manejado visualmente.

✔️ 8. Contiene pruebas integradas

El proyecto incorpora tres casos de prueba predefinidos:

Columna corta que cumple

Columna esbelta donde gobierna Euler

Columna que falla por exceder su capacidad

Sirven para verificar el funcionamiento del modelo.

📄 Resumen general

Este proyecto combina:

Modelado estructural

Programación modular en Python

Interfaz gráfica intuitiva

Automatización de cálculos y pruebas

Permitiendo realizar un análisis axial completo de columnas de manera práctica, visual y verificable.
