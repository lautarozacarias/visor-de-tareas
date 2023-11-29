import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import random
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

ventana = tk.Tk()
ventana.title(config.get('MainWindow', 'title'))
ventana.geometry(config.get('MainWindow', 'geometry'))

barra_menu = tk.Menu(ventana)
ventana.config(menu=barra_menu)

procesos = []

def mostrar_propiedades(event):
    seleccion = lista_tareas.selection()

    if seleccion:
        proceso_seleccionado = seleccion[0]
        proceso_info = lista_tareas.item(proceso_seleccionado, "values")

        mensaje = f"PID: {proceso_info[0]}\nNombre: {proceso_info[1]}\nUso de CPU: {proceso_info[2]}\nMemoria: {proceso_info[3]}\nEspacio en Disco: {proceso_info[4]}"

        try:
            proceso = psutil.Process(int(proceso_info[0]))
            ruta_ejecutable = proceso.exe()
            mensaje += f"\nRuta Ejecutable: {ruta_ejecutable}"
        except psutil.NoSuchProcess:
            mensaje += "\nRuta Ejecutable: No disponible"

        mensaje += "\n\nSubprocesos:\n"
        subprocesos = obtener_subprocesos(int(proceso_info[0]))
        for subproceso in subprocesos:
            mensaje += f"PID: {subproceso[0]}\nNombre: {subproceso[1]}\nUso de CPU: {subproceso[2]}\nMemoria: {subproceso[3]}\nEspacio en Disco: {subproceso[4]}\n"

        messagebox.showinfo("Propiedades del Proceso", mensaje)

def cambiar():
    colores = ['#FF5733', '#33FF57', '#5733FF', '#FFFF33', '#33FFFF']
    ventana.config(bg=random.choice(colores))

def obtener_subprocesos(pid):
    subprocesos = []
    for proceso in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'io_counters', 'ppid']):
        proceso_info = proceso.info
        if proceso_info['ppid'] == pid:
            memoria = proceso_info['memory_percent']
            disco = proceso_info['io_counters'].write_bytes / (1024 * 1024)  
            subprocesos.append((proceso_info['pid'], proceso_info['name'], proceso_info['cpu_percent'], memoria, disco))
    return subprocesos

def ordenar_por_cpu():
    global procesos
    procesos.sort(key=lambda x: x[2], reverse=True)
    cargar_lista(procesos)

def ordenar_por_memoria():
    global procesos
    procesos.sort(key=lambda x: x[3], reverse=True)
    cargar_lista(procesos)

def ordenar_por_disco():
    global procesos
    procesos.sort(key=lambda x: x[4], reverse=True)
    cargar_lista(procesos)

def cargar_lista(proceso_lista):
    lista_tareas.delete(*lista_tareas.get_children())
    for proceso_info in proceso_lista:
        memoria = proceso_info[3]
        disco = proceso_info[4]
        lista_tareas.insert("", "end", values=(proceso_info[0], proceso_info[1], f"{proceso_info[2]:.2f}%", f"{memoria:.2f}%", f"{disco:.2f} MB"))

def listar_procesos():
    global procesos
    procesos = []

    for proceso in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'io_counters']):
        proceso_info = proceso.info
        try:
            memoria = proceso_info['memory_percent']
            disco = proceso_info['io_counters'].write_bytes / (1024 * 1024)  
            procesos.append((proceso_info['pid'], proceso_info['name'], proceso_info['cpu_percent'], memoria, disco))
        except KeyError:
            pass

    cargar_lista(procesos)

def mostrar_ayuda():
    mensaje_ayuda = "Bienvenido a la ventana de ayuda.\n\nCon el botón de  'Listar Procesos' mostrara los procesos que se estén ejecutando en ese momento\n\nCon doble clic en uso de CPU ordenara los procesos de mayor a menor y asi con los demas \n\nCon doble clic sobre un proceso se mostrara sus propiedades"
    messagebox.showinfo("Ayuda", mensaje_ayuda)
    
def mostrar_Acerca():
    mensaje_Acerca = "Acerca de Un visor de tareas es una herramienta que proporciona información detallada sobre los procesos en ejecución en un sistema informático. \n Este software muestra datos cruciales como el identificador de proceso (PID), nombre, uso de CPU, consumo de memoria y espacio en disco de cada proceso. \n La información se presenta generalmente en una interfaz gráfica que facilita la monitorización y gestión de las tareas en tiempo real."
    messagebox.showinfo("Acerca De", mensaje_Acerca)



frame_principal = ttk.Frame(ventana)
frame_principal.grid(row=0, column=0, padx=20, pady=20)

boton_listar = ttk.Button(frame_principal, text="Listar procesos", command=listar_procesos)
boton_listar.grid(row=0, column=0, pady=10)

columnas = ("PID", "Nombre", "Uso de CPU", "Memoria", "Espacio en Disco (MB)")
lista_tareas = ttk.Treeview(frame_principal, columns=columnas, show="headings", height=15)
for col in columnas:
    lista_tareas.heading(col, text=col)
    lista_tareas.column(col, width=150)
    if col == "Uso de CPU":
        lista_tareas.heading(col, text=col, command=ordenar_por_cpu)
    elif col == "Memoria":
        lista_tareas.heading(col, text=col, command=ordenar_por_memoria)
    elif col == "Espacio en Disco (MB)":
        lista_tareas.heading(col, text=col, command=ordenar_por_disco)
lista_tareas.grid(row=1, column=0)

scroll_y = ttk.Scrollbar(frame_principal, orient="vertical", command=lista_tareas.yview)
scroll_y.grid(row=1, column=1, sticky="ns")
lista_tareas.config(yscrollcommand=scroll_y.set)

lista_tareas.bind("<Double-1>", mostrar_propiedades)

frame_principal.grid_rowconfigure(1, weight=1)
frame_principal.grid_columnconfigure(0, weight=1)

menu_file = tk.Menu(barra_menu, tearoff=0)
barra_menu.add_cascade(label="Ayuda", menu=menu_file)
menu_file.add_command(label="Funcionamiento", command=mostrar_ayuda)
menu_file.add_command(label="Acerca De ", command=mostrar_Acerca)
menu_file.add_command(label="Cambiar de Color ", command=cambiar)

ventana.mainloop()

