from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    ventas = db.relationship("Venta", backref="usuario", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email
        }



class Producto(db.Model):
    __tablename__ = "productos"

    activo = db.Column(db.Boolean, default=True)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    ventas = db.relationship("Venta", backref="producto", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock
        }


class Venta(db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.utcnow() - timedelta(hours=3))
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "producto": self.producto.nombre,
            "cantidad": self.cantidad,
            "total": self.total,
            "fecha": self.fecha.strftime("%d/%m/%Y %H:%M")
        }