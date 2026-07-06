class Producto:
    def __init__(self, id_producto, nombre, precio, stock):
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = precio
        self.__stock = stock  # atributo privado

    def get_stock(self):
        return self.__stock

    def set_stock(self, cantidad):
        if cantidad < 0:
            print("Error: el stock no puede ser negativo.")
        else:
            self.__stock = cantidad

    def aumentar_stock(self, cantidad):
        if cantidad <= 0:
            print("Error: la cantidad debe ser mayor a cero.")
        else:
            self.__stock += cantidad
            print("Stock actualizado correctamente.")

    def descontar_stock(self, cantidad):
        if cantidad <= 0:
            print("Error: la cantidad debe ser mayor a cero.")
            return False

        if self.__stock == 0:
            print("Error: no hay stock disponible.")
            return False

        if cantidad > self.__stock:
            print("Error: stock insuficiente.")
            return False

        self.__stock -= cantidad
        return True

    def mostrar_info(self):
        print(f"ID: {self.id_producto}")
        print(f"Nombre: {self.nombre}")
        print(f"Precio: ${self.precio}")
        print(f"Stock: {self.__stock}")
        print("------------------------")


class Inventario:
    def __init__(self):
        self.productos = []

    def agregar_producto(self, producto):
        self.productos.append(producto)
        print("Producto agregado correctamente.")

    def buscar_producto(self, id_producto):
        for producto in self.productos:
            if producto.id_producto == id_producto:
                return producto
        return None

    def mostrar_inventario(self):
        if len(self.productos) == 0:
            print("El inventario está vacío.")
        else:
            print("\n--- INVENTARIO ACTUAL ---")
            for producto in self.productos:
                producto.mostrar_info()


class Foodtruck:
    def __init__(self, nombre):
        self.nombre = nombre
        self.inventario = Inventario()

    def agregar_producto(self):
        print("\n--- AGREGAR PRODUCTO ---")

        id_producto = int(input("Ingrese ID del producto: "))
        nombre = input("Ingrese nombre del producto: ")
        precio = float(input("Ingrese precio del producto: "))
        stock = int(input("Ingrese stock inicial: "))

        if stock < 0:
            print("Error: el stock inicial no puede ser negativo.")
            return

        producto = Producto(id_producto, nombre, precio, stock)
        self.inventario.agregar_producto(producto)

    def registrar_venta(self):
        print("\n--- REGISTRAR VENTA ---")

        id_producto = int(input("Ingrese ID del producto vendido: "))
        cantidad = int(input("Ingrese cantidad vendida: "))

        producto = self.inventario.buscar_producto(id_producto)

        if producto is None:
            print("Error: producto no encontrado.")
            return

        venta_realizada = producto.descontar_stock(cantidad)

        if venta_realizada:
            total = producto.precio * cantidad
            print("Venta registrada correctamente.")
            print(f"Total de la venta: ${total}")

    def mostrar_inventario(self):
        self.inventario.mostrar_inventario()


def menu():
    foodtruck = Foodtruck("SmartGastro Foodtruck")

    while True:
        print("\n===== SMARTGASTRO =====")
        print("1. Agregar producto al inventario")
        print("2. Registrar venta")
        print("3. Mostrar inventario")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            foodtruck.agregar_producto()
        elif opcion == "2":
            foodtruck.registrar_venta()
        elif opcion == "3":
            foodtruck.mostrar_inventario()
        elif opcion == "4":
            print("Saliendo del sistema SmartGastro...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


menu()