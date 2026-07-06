from app import app
from models import db, Usuario
from werkzeug.security import generate_password_hash


with app.app_context():
    db.create_all()

    email = "admin@smartgastro.com"
    password = "admin123"

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        usuario.nombre = "Administrador"
        usuario.password_hash = generate_password_hash(password)
        print("Admin actualizado.")
    else:
        usuario = Usuario(
            nombre="Administrador",
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(usuario)
        print("Admin creado.")

    db.session.commit()

    print("Email:", email)
    print("Password:", password)