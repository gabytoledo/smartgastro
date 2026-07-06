import os
from datetime import datetime, date
from services.pdf_service import generar_pdf_ventas
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    redirect,
    url_for,
    session,
    send_file
)

from dotenv import load_dotenv
from werkzeug.security import check_password_hash

from models import db, Producto, Venta, Usuario


load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "clave_temporal_smartgastro"
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(BASE_DIR, "smartgastro.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)






limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["300 per hour"]
)






ubicacion_actual = {
    "latitud": -34.6037,
    "longitud": -58.3816
}

from functools import wraps


def login_requerido(funcion):
    @wraps(funcion)
    def wrapper(*args, **kwargs):

        if "usuario_id" not in session:
            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return wrapper

def obtener_alerta_clima():

    try:
        url = "https://api.open-meteo.com/v1/forecast"

        parametros = {
            "latitude": ubicacion_actual["latitud"],
            "longitude": ubicacion_actual["longitud"],
            "current": "temperature_2m,precipitation,rain,weather_code,wind_speed_10m",
            "timezone": "America/Argentina/Buenos_Aires"
        }

        respuesta = requests.get(url, params=parametros, timeout=5)
        datos = respuesta.json()

        clima_actual = datos["current"]

        temperatura = clima_actual["temperature_2m"]
        lluvia = clima_actual["rain"]
        precipitacion = clima_actual["precipitation"]
        viento = clima_actual["wind_speed_10m"]
        codigo = clima_actual["weather_code"]
        descripcion_clima = interpretar_codigo_clima(codigo)
        hay_lluvia = lluvia > 0 or precipitacion > 0 or codigo in [
            51, 53, 55,
            61, 63, 65,
            80, 81, 82,
            95, 96, 99
        ]

        if hay_lluvia:
            return {
                "disponible": True,
                "alerta": True,
                "mensaje": "Alerta de lluvia: se recomienda producir menos stock para evitar merma.",
                "temperatura": temperatura,
                "lluvia": lluvia,
                "viento": viento,
                "descripcion": descripcion_clima["descripcion"],
                "emoji": descripcion_clima["emoji"],
                "riesgo": "Alto",
                "clase_clima": "weather-rain"
            }

        return {
            "disponible": True,
            "alerta": False,
            "mensaje": "Clima estable: producción normal recomendada.",
            "temperatura": temperatura,
            "lluvia": lluvia,
            "viento": viento,
            "descripcion": descripcion_clima["descripcion"],
            "emoji": descripcion_clima["emoji"],
            "riesgo": "Bajo",
            "clase_clima": "weather-clear"
        }

    except Exception:
        return {
            "disponible": False,
            "alerta": False,
            "mensaje": "No se pudo consultar el clima.",
            "temperatura": None,
            "lluvia": None,
            "viento": None,
            "riesgo": "Desconocido",
            "clase_clima": "weather-unknown"
        }
    


def interpretar_codigo_clima(codigo):

    codigos = {
        0: {"descripcion": "Cielo despejado", "emoji": "☀️"},
        1: {"descripcion": "Mayormente despejado", "emoji": "🌤️"},
        2: {"descripcion": "Parcialmente nublado", "emoji": "⛅"},
        3: {"descripcion": "Nublado", "emoji": "☁️"},

        45: {"descripcion": "Niebla", "emoji": "🌫️"},
        48: {"descripcion": "Niebla con escarcha", "emoji": "🌫️"},

        51: {"descripcion": "Llovizna leve", "emoji": "🌦️"},
        53: {"descripcion": "Llovizna moderada", "emoji": "🌦️"},
        55: {"descripcion": "Llovizna intensa", "emoji": "🌧️"},

        61: {"descripcion": "Lluvia leve", "emoji": "🌧️"},
        63: {"descripcion": "Lluvia moderada", "emoji": "🌧️"},
        65: {"descripcion": "Lluvia intensa", "emoji": "🌧️"},

        66: {"descripcion": "Lluvia helada leve", "emoji": "🧊"},
        67: {"descripcion": "Lluvia helada intensa", "emoji": "🧊"},

        71: {"descripcion": "Nieve leve", "emoji": "❄️"},
        73: {"descripcion": "Nieve moderada", "emoji": "🌨️"},
        75: {"descripcion": "Nieve intensa", "emoji": "🌨️"},

        77: {"descripcion": "Granizo pequeño", "emoji": "🧊"},

        80: {"descripcion": "Chaparrones leves", "emoji": "🌦️"},
        81: {"descripcion": "Chaparrones moderados", "emoji": "🌧️"},
        82: {"descripcion": "Chaparrones violentos", "emoji": "⛈️"},

        85: {"descripcion": "Nevadas leves", "emoji": "🌨️"},
        86: {"descripcion": "Nevadas intensas", "emoji": "❄️"},

        95: {"descripcion": "Tormenta", "emoji": "⛈️"},
        96: {"descripcion": "Tormenta con granizo leve", "emoji": "⛈️"},
        99: {"descripcion": "Tormenta con granizo fuerte", "emoji": "⛈️"}
    }

    return codigos.get(
        codigo,
        {"descripcion": "Clima no identificado", "emoji": "🌡️"}
    )




def obtener_nombre_ubicacion(latitud, longitud):

    try:
        url = "https://nominatim.openstreetmap.org/reverse"

        parametros = {
            "lat": latitud,
            "lon": longitud,
            "format": "json",
            "accept-language": "es"
        }

        headers = {
            "User-Agent": "SmartGastroTP/1.0"
        }

        respuesta = requests.get(
            url,
            params=parametros,
            headers=headers,
            timeout=5
        )

        datos = respuesta.json()
        direccion = datos.get("address", {})

        barrio = direccion.get("suburb") or direccion.get("neighbourhood")
        ciudad = (
            direccion.get("city")
            or direccion.get("town")
            or direccion.get("municipality")
            or direccion.get("county")
        )
        provincia = direccion.get("state")

        partes = [
            parte
            for parte in [barrio, ciudad, provincia]
            if parte
        ]

        if partes:
            return " · ".join(partes)

        return datos.get("display_name", "Ubicación detectada")

    except Exception:
        return "Ubicación no identificada"





@app.route("/api/ubicacion", methods=["POST"])
@login_requerido
@limiter.limit("20 per minute")
def guardar_ubicacion():

    global ubicacion_actual

    datos = request.json

    try:
        ubicacion_actual["latitud"] = float(datos["latitud"])
        ubicacion_actual["longitud"] = float(datos["longitud"])

        return jsonify({
            "mensaje": "Ubicación actualizada correctamente",
            "ubicacion": ubicacion_actual
        })

    except Exception as error:
        return jsonify({
            "error": "No se pudo actualizar la ubicación",
            "detalle": str(error)
        }), 400
# =========================
# RUTAS DE AUTENTICACIÓN
# =========================

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password_hash, password):

            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Email o contraseña incorrectos"
        )

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================
# RUTAS WEB
# =========================
@app.route("/ventas/pdf/<periodo>")
@login_requerido
@limiter.limit("10 per minute")
def descargar_pdf_ventas(periodo):

    hoy = date.today()

    query = Venta.query

    titulo_periodo = "Todo el historial"

    if periodo == "hoy":
        inicio = datetime(hoy.year, hoy.month, hoy.day, 0, 0, 0)
        fin = datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59)

        query = query.filter(Venta.fecha >= inicio, Venta.fecha <= fin)
        titulo_periodo = "Ventas de hoy"

    elif periodo == "mes":
        inicio = datetime(hoy.year, hoy.month, 1, 0, 0, 0)

        query = query.filter(Venta.fecha >= inicio)
        titulo_periodo = "Ventas del mes actual"

    elif periodo == "anio":
        inicio = datetime(hoy.year, 1, 1, 0, 0, 0)

        query = query.filter(Venta.fecha >= inicio)
        titulo_periodo = "Ventas del año actual"

    elif periodo == "todo":
        pass

    else:
        return "Período inválido", 400

    ventas = query.order_by(Venta.fecha.desc()).all()

    pdf = generar_pdf_ventas(
        ventas=ventas,
        titulo_periodo=titulo_periodo
    )

    return send_file(
        pdf,
        as_attachment=True,
        download_name=f"reporte_ventas_{periodo}_smartgastro.pdf",
        mimetype="application/pdf"
    )



@app.route("/")
@login_requerido
def home():
    from datetime import datetime

    productos = Producto.query.filter_by(activo=True).all()
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    clima = obtener_alerta_clima()

    nombre_ubicacion = obtener_nombre_ubicacion(
    ubicacion_actual["latitud"],
    ubicacion_actual["longitud"]
    )

    cantidad_productos = Producto.query.count()
    cantidad_ventas = Venta.query.count()

    valor_stock = sum(
        producto.precio * producto.stock
        for producto in productos
    )

    stock_total = sum(
        producto.stock
        for producto in productos
    )

    ultima_actualizacion = datetime.now().strftime("%H:%M:%S")

    return render_template(
    
    "productos.html",
    productos=productos,
    ventas=ventas,
    clima=clima,
    cantidad_productos=cantidad_productos,
    cantidad_ventas=cantidad_ventas,
    valor_stock=valor_stock,
    stock_total=stock_total,
    ubicacion=ubicacion_actual,
    nombre_ubicacion=nombre_ubicacion,
    ultima_actualizacion=ultima_actualizacion,
)
@app.route("/productos/crear", methods=["POST"])
@login_requerido
def crear_producto_web():

    try:
        nuevo_producto = Producto(
            nombre=request.form["nombre"],
            precio=float(request.form["precio"]),
            stock=int(request.form["stock"])
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return redirect(url_for("home"))

    except Exception as error:
        db.session.rollback()
        return f"Error al crear producto: {error}", 400


@app.route("/productos/eliminar/<int:id_producto>")
@login_requerido
def eliminar_producto_web(id_producto):

    producto = Producto.query.get_or_404(id_producto)

    try:
        producto.activo = False
        db.session.commit()

        return redirect(url_for("home"))

    except Exception as error:
        db.session.rollback()
        return f"Error al dar de baja producto: {error}", 400
    


@app.route("/productos/editar/<int:id_producto>")
@login_requerido
def editar_producto(id_producto):

    producto = Producto.query.get_or_404(id_producto)

    return render_template(
        "editar_producto.html",
        producto=producto
    )


@app.route("/productos/actualizar/<int:id_producto>", methods=["POST"])
@login_requerido
def actualizar_producto_web(id_producto):

    producto = Producto.query.get_or_404(id_producto)

    try:
        producto.nombre = request.form["nombre"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])

        db.session.commit()

        return redirect(url_for("home"))

    except Exception as error:
        db.session.rollback()
        return f"Error al actualizar producto: {error}", 400


# =========================
# API PRODUCTOS
# =========================

@app.route("/api/productos", methods=["GET"])
@login_requerido
def obtener_productos():

    productos = Producto.query.all()

    return jsonify([
        producto.to_dict()
        for producto in productos
    ])


@app.route("/api/productos", methods=["POST"])
@login_requerido
@limiter.limit("40 per minute")
def agregar_producto():




    datos = request.json
    
    try:
        nuevo_producto = Producto(
            nombre=datos["nombre"],
            precio=float(datos["precio"]),
            stock=int(datos["stock"])
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return jsonify({
            "mensaje": "Producto agregado correctamente",
            "producto": nuevo_producto.to_dict()
        }), 201

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "error": "No se pudo agregar el producto",
            "detalle": str(error)
        }), 400


@app.route("/api/productos/<int:id_producto>", methods=["PATCH"])
@login_requerido
def actualizar_producto(id_producto):

    producto = Producto.query.get(id_producto)

    if producto is None:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404

    datos = request.json

    try:
        if "nombre" in datos:
            producto.nombre = datos["nombre"]

        if "precio" in datos:
            producto.precio = float(datos["precio"])

        if "stock" in datos:
            producto.stock = int(datos["stock"])

        db.session.commit()

        return jsonify({
            "mensaje": "Producto actualizado",
            "producto": producto.to_dict()
        })

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "error": str(error)
        }), 400


@app.route("/productos/vender/<int:id_producto>", methods=["POST"])
@login_requerido
def vender_producto(id_producto):
    
    producto = Producto.query.get_or_404(id_producto)

    try:
        cantidad = int(request.form["cantidad"])

        if cantidad <= 0:
            return "La cantidad debe ser mayor a cero", 400

        if cantidad > producto.stock:
            return "Stock insuficiente", 400

        total = producto.precio * cantidad

        nueva_venta = Venta(
            producto_id=producto.id,
            usuario_id=session["usuario_id"],
            cantidad=cantidad,
            total=total
        )

        producto.stock -= cantidad

        db.session.add(nueva_venta)
        db.session.commit()

        return redirect(url_for("home") + "#ventas")

    except Exception as error:
        db.session.rollback()
        return f"Error al registrar venta: {error}", 400


@app.route("/api/productos/<int:id_producto>", methods=["DELETE"])
@login_requerido
def eliminar_producto(id_producto):

    producto = Producto.query.get(id_producto)

    if producto is None:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404

    try:
        producto.activo = False
        db.session.commit()

        return jsonify({
            "mensaje": "Producto dado de baja correctamente"
        })

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "error": str(error)
        }), 400


@app.route("/api/productos/<int:id_producto>/vender", methods=["POST"])
@login_requerido
def vender_producto_api(id_producto):

    producto = Producto.query.get(id_producto)

    if producto is None:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404

    datos = request.json

    try:
        cantidad = int(datos["cantidad"])

        if cantidad <= 0:
            return jsonify({
                "error": "La cantidad debe ser mayor a cero"
            }), 400

        if cantidad > producto.stock:
            return jsonify({
                "error": "Stock insuficiente"
            }), 400

        total = producto.precio * cantidad

        nueva_venta = Venta(
            producto_id=producto.id,
            usuario_id=session["usuario_id"],
            cantidad=cantidad,
            total=total
        )

        producto.stock -= cantidad

        db.session.add(nueva_venta)
        db.session.commit()

        return jsonify({
            "mensaje": "Venta registrada correctamente",
            "producto": producto.to_dict(),
            "venta": nueva_venta.to_dict()
        }), 201

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "error": "No se pudo registrar la venta",
            "detalle": str(error)
        }), 400













# =========================
# EJECUCIÓN
# =========================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)