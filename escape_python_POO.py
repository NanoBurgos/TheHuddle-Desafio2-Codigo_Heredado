import tkinter as tk
from tkinter import messagebox
import random

TAMANO_CELDA = 40

class Mapa:
    def __init__(self, filas, columnas, inicio, meta, canvas, ventana):
        self.filas = filas
        self.columnas = columnas
        self.inicio = inicio
        self.meta = meta
        self.tablero = [[0 for _ in range(columnas)] for _ in range(filas)]
        self.canvas = canvas
        self.ventana = ventana
        self.ruta_actual = None               
        self.recalcular_callback = None      

    def celda_valida(self, fila, columna):
        return 0 <= fila < self.filas and 0 <= columna < self.columnas

    def generar_obstaculos_aleatorios(self):
        tipos = [1, 2, 3]
        for f in range(self.filas):
            for c in range(self.columnas):
                if (f, c) in [self.inicio, self.meta]:
                    continue
                if random.random() < 0.2:
                    self.tablero[f][c] = random.choice(tipos)
                    if self.tablero[f][c] == 3:
                        self.ventana.after(5000, lambda fila=f, col=c: self.limpiar_bloque_temporal(fila, col))

    def limpiar_bloque_temporal(self, fila, columna):
        if self.tablero[fila][columna] == 3:
            self.tablero[fila][columna] = 0

            if callable(self.recalcular_callback):
                self.ventana.after(0, self.recalcular_callback)
            else:
                self.dibujar(self.ruta_actual)

    def dibujar(self, ruta=None):
        self.canvas.delete("all")
        colores = {0: "white", 1: "black", 2: "aqua", 3: "orange"}

        for f in range(self.filas):
            for c in range(self.columnas):
                color = colores[self.tablero[f][c]]
                x1, y1 = c * TAMANO_CELDA, f * TAMANO_CELDA
                x2, y2 = x1 + TAMANO_CELDA, y1 + TAMANO_CELDA
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

        # Inicio y meta
        self._dibujar_celda(self.inicio, "green")
        self._dibujar_celda(self.meta, "red")

        # Ruta (si existe)
        if ruta:
            for f, c in ruta:
                if (f, c) not in [self.inicio, self.meta]:
                    self._dibujar_celda((f, c), "blue")

    def _dibujar_celda(self, coord, color):
        x1, y1 = coord[1] * TAMANO_CELDA, coord[0] * TAMANO_CELDA
        self.canvas.create_rectangle(x1, y1, x1 + TAMANO_CELDA, y1 + TAMANO_CELDA, fill=color)


class CalculadoraDeRutas:
    def __init__(self, mapa):
        self.mapa = mapa

    def heuristica(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def vecinos(self, fila, columna):
        posibles = [(fila-1, columna), (fila+1, columna), (fila, columna-1), (fila, columna+1)]
        return [
            (f, c)
            for f, c in posibles
            if self.mapa.celda_valida(f, c) and self.mapa.tablero[f][c] != 1
        ]

    def ejecutar_a_estrella(self):
        inicio, meta = self.mapa.inicio, self.mapa.meta
        abiertos = [inicio]
        camino_previo = {}
        costos = [[float("inf")] * self.mapa.columnas for _ in range(self.mapa.filas)]
        puntajes = [[float("inf")] * self.mapa.columnas for _ in range(self.mapa.filas)]

        costos[inicio[0]][inicio[1]] = 0
        puntajes[inicio[0]][inicio[1]] = self.heuristica(inicio, meta)

        while abiertos:
            abiertos.sort(key=lambda cel: puntajes[cel[0]][cel[1]])
            actual = abiertos.pop(0)

            if actual == meta:
                ruta = [meta]
                while ruta[-1] in camino_previo:
                    ruta.append(camino_previo[ruta[-1]])
                ruta = ruta[::-1] 
                self.mapa.ruta_actual = ruta
                self.mapa.dibujar(self.mapa.ruta_actual)
                return

            for f, c in self.vecinos(*actual):
                costo_mov = 1
                if self.mapa.tablero[f][c] == 2:
                    costo_mov = 2
                elif self.mapa.tablero[f][c] == 3:
                    costo_mov = 5

                nuevo_costo = costos[actual[0]][actual[1]] + costo_mov
                if nuevo_costo < costos[f][c]:
                    costos[f][c] = nuevo_costo
                    puntajes[f][c] = nuevo_costo + self.heuristica((f, c), meta)
                    camino_previo[(f, c)] = actual
                    if (f, c) not in abiertos:
                        abiertos.append((f, c))

        self.mapa.ruta_actual = None
        messagebox.showinfo("Ruta", "No hay ruta posible")


class JuegoGUI:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Escape de Coordenadas - Luciano Burgos")

        # Widgets
        self._crear_widgets()

        self.mapa = None
        self.rutas = None

    def _crear_widgets(self):
        self.label_filas = tk.Label(self.ventana, text="Filas:")
        self.label_filas.grid(row=0, column=0)
        self.entry_filas = tk.Entry(self.ventana)
        self.entry_filas.insert(0, "10")
        self.entry_filas.grid(row=0, column=1)

        self.label_columnas = tk.Label(self.ventana, text="Columnas:")
        self.label_columnas.grid(row=0, column=2)
        self.entry_columnas = tk.Entry(self.ventana)
        self.entry_columnas.insert(0, "10")
        self.entry_columnas.grid(row=0, column=3)

        self.label_inicio = tk.Label(self.ventana, text="Inicio (fila,col):")
        self.label_inicio.grid(row=1, column=0)
        self.entry_inicio = tk.Entry(self.ventana)
        self.entry_inicio.insert(0, "0,0")
        self.entry_inicio.grid(row=1, column=1)

        self.label_meta = tk.Label(self.ventana, text="Meta (fila,col):")
        self.label_meta.grid(row=1, column=2)
        self.entry_meta = tk.Entry(self.ventana)
        self.entry_meta.insert(0, "9,9")
        self.entry_meta.grid(row=1, column=3)

        self.boton_crear = tk.Button(self.ventana, text="Crear mapa", command=self.crear_mapa)
        self.boton_crear.grid(row=2, column=0, columnspan=4)

        self.label_info = tk.Label(
            self.ventana,
            text="Clic en las celdas para cambiar terreno:\n0=Libre, 1=Edificio, 2=Agua, 3=Bloque temporal (desaparece en 5s)"
        )
        self.label_info.grid(row=3, column=0, columnspan=4)

        self.canvas = tk.Canvas(self.ventana, width=400, height=400, bg="white")
        self.canvas.grid(row=4, column=0, columnspan=4)

    def crear_mapa(self):
        try:
            filas = int(self.entry_filas.get())
            columnas = int(self.entry_columnas.get())
        except ValueError:
            messagebox.showerror("Error", "Filas/columnas deben ser números enteros")
            return

        try:
            inicio = tuple(map(int, self.entry_inicio.get().split(",")))
            meta = tuple(map(int, self.entry_meta.get().split(",")))
        except Exception:
            messagebox.showerror("Error", "Coordenadas inválidas")
            return

        if filas <= 0 or columnas <= 0:
            messagebox.showerror("Error", "Filas y columnas deben ser mayores que cero")
            return

        self.canvas.config(width=columnas * TAMANO_CELDA, height=filas * TAMANO_CELDA)

        self.mapa = Mapa(filas, columnas, inicio, meta, self.canvas, self.ventana)
        self.rutas = CalculadoraDeRutas(self.mapa)

        self.mapa.recalcular_callback = self.rutas.ejecutar_a_estrella

        if not (self.mapa.celda_valida(*inicio) and self.mapa.celda_valida(*meta)):
            messagebox.showerror("Error", "Inicio o meta fuera del mapa")
            return

        self.mapa.generar_obstaculos_aleatorios()
        self.rutas.ejecutar_a_estrella()
        self.canvas.bind("<Button-1>", self.click_celda)

    def click_celda(self, evento):
        columna = evento.x // TAMANO_CELDA
        fila = evento.y // TAMANO_CELDA

        if not self.mapa.celda_valida(fila, columna):
            return
        if (fila, columna) in [self.mapa.inicio, self.mapa.meta]:
            return

        # Cambiamos el tipo de terreno con cada click
        self.mapa.tablero[fila][columna] = (self.mapa.tablero[fila][columna] + 1) % 4

        if self.mapa.tablero[fila][columna] == 3:
            self.ventana.after(5000, lambda f=fila, c=columna: self.mapa.limpiar_bloque_temporal(f, c))

        # Al modificar manualmente el mapa, recalculamos A* y actualizamos ruta_actual
        self.rutas.ejecutar_a_estrella()

    def run(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    app = JuegoGUI()
    app.run()