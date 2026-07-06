import tkinter as tk
from tkinter import messagebox


class Producto:
    def __init__(self, id_producto, nombre, precio, stock):
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = precio
        self.__stock = stock

    def get_stock(self):
        return self.__stock

    def descontar_stock(self, cantidad):
        if cantidad <= 0:
            return False

        if cantidad > self.__stock:
            return False

        self.__stock -= cantidad
        return True

    def aumentar_stock(self, cantidad):
        self.__stock += cantidad


class Inventario:
    def __init__(self):
        self.productos = []

    def agregar_producto(self, producto):
        self.productos.append(producto)

    def buscar_producto(self, id_producto):
        for producto in self.productos:
            if producto.id_producto == id_producto:
                return producto
        return None


class SmartGastroGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("SmartGastro")
        self.root.geometry("600x500")

        self.inventario = Inventario()

        titulo = tk.Label(root, text="SMARTGASTRO", font=("Arial", 20, "bold"))
        titulo.pack(pady=10)

        # FRAME PRODUCTO
        frame_producto = tk.Frame(root)
        frame_producto.pack(pady=10)

        tk.Label(frame_producto, text="ID").grid(row=0, column=0)
        tk.Label(frame_producto, text="Nombre").grid(row=1, column=0)
        tk.Label(frame_producto, text="Precio").grid(row=2, column=0)
        tk.Label(frame_producto, text="Stock").grid(row=3, column=0)

        self.entry_id = tk.Entry(frame_producto)
        self.entry_nombre = tk.Entry(frame_producto)
        self.entry_precio = tk.Entry(frame_producto)
        self.entry_stock = tk.Entry(frame_producto)

        self.entry_id.grid(row=0, column=1)
        self.entry_nombre.grid(row=1, column=1)
        self.entry_precio.grid(row=2, column=1)
        self.entry_stock.grid(row=3, column=1)

        btn_agregar = tk.Button(
            root,
            text="Agregar Producto",
            command=self.agregar_producto
        )
        btn_agregar.pack(pady=10)

        # FRAME VENTA
        frame_venta = tk.Frame(root)
        frame_venta.pack(pady=10)

        tk.Label(frame_venta, text="ID Producto Venta").grid(row=0, column=0)
        tk.Label(frame_venta, text="Cantidad").grid(row=1, column=0)

        self.entry_venta_id = tk.Entry(frame_venta)
        self.entry_venta_cantidad = tk.Entry(frame_venta)

        self.entry_venta_id.grid(row=0, column=1)
        self.entry_venta_cantidad.grid(row=1, column=1)

        btn_vender = tk.Button(
            root,
            text="Registrar Venta",
            command=self.registrar_venta
        )
        btn_vender.pack(pady=10)

        # LISTA INVENTARIO
        self.lista = tk.Listbox(root, width=70, height=12)
        self.lista.pack(pady=10)

        btn_actualizar = tk.Button(
            root,
            text="Mostrar Inventario",
            command=self.mostrar_inventario
        )
        btn_actualizar.pack(pady=10)

    def agregar_producto(self):
        try:
            id_producto = int(self.entry_id.get())
            nombre = self.entry_nombre.get()
            precio = float(self.entry_precio.get())
            stock = int(self.entry_stock.get())

            producto = Producto(id_producto, nombre, precio, stock)
            self.inventario.agregar_producto(producto)

            messagebox.showinfo("Éxito", "Producto agregado correctamente")

            self.limpiar_campos()

        except:
            messagebox.showerror("Error", "Datos inválidos")

    def registrar_venta(self):
        try:
            id_producto = int(self.entry_venta_id.get())
            cantidad = int(self.entry_venta_cantidad.get())

            producto = self.inventario.buscar_producto(id_producto)

            if producto is None:
                messagebox.showerror("Error", "Producto no encontrado")
                return

            if producto.descontar_stock(cantidad):
                total = producto.precio * cantidad
                messagebox.showinfo(
                    "Venta realizada",
                    f"Venta registrada\nTotal: ${total}"
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Stock insuficiente"
                )

            self.mostrar_inventario()

        except:
            messagebox.showerror("Error", "Datos inválidos")

    def mostrar_inventario(self):
        self.lista.delete(0, tk.END)

        for producto in self.inventario.productos:
            texto = (
                f"ID: {producto.id_producto} | "
                f"Nombre: {producto.nombre} | "
                f"Precio: ${producto.precio} | "
                f"Stock: {producto.get_stock()}"
            )

            self.lista.insert(tk.END, texto)

    def limpiar_campos(self):
        self.entry_id.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)


root = tk.Tk()
app = SmartGastroGUI(root)
root.mainloop()