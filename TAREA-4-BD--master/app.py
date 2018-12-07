from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
#importo una biblioteca para los passwords y la seguridad
from werkzeug.security import  generate_password_hash
from werkzeug.security import check_password_hash

import os

dbdir= "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
db = SQLAlchemy(app)

#Sql me permite cominicarme con el por medio de clases en python
class personas(db.Model):
    apodo = db.Column(db.String(50), primary_key=True)
    #ojo que no necesitamos que las claves sean unicas
    password = db.Column(db.String(80), nullable=False)
    nativo = db.Column(db.String(80), nullable=False)
    contacto = db.Column(db.Integer, nullable=False)
    ventas = db.Column(db.Integer, nullable=True)
    compras = db.Column(db.Integer, nullable=False)

class cuenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Integer, nullable=False)
    gastado = db.Column(db.Integer, nullable=False)
    saldo = db.Column(db.String(255), nullable=False)

class objeto(db.Model):
    nombre = db.Column(db.String(126), primary_key=True)
    legalidad = db.Column(db.Boolean, nullable=False)
    codigo = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    duenos = db.Column(db.Integer, nullable=False)

class policia(db.Model):
    placa = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(126), nullable=False)
    soborno = db.Column(db.Date, nullable=False)

class sector(db.Model):
    numero = db.Column(db.Integer, primary_key=True)
    ubicacion = db.Column(db.String(126), nullable=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    nombre = request.args.get("nickname")
    user = personas.query.filter_by(apodo=nombre).first()
    if user:
        return render_template("cuenta.html", nombre = nombre)

    else:
        return "El usuario no existe"



@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        #hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        new_user = personas(apodo=request.form["username"], password=request.form["password"], nativo=request.form["native"], contacto=request.form["contact"], ventas=0, compras=0)
        db.session.add(new_user)
        #nos confirma cadad uno de los cambios
        db.session.commit()
        return "ya te has registrado exitosamente "
    return  render_template("signup.html")

@app.route("/login",methods=["GET","POST"])
def login():
#request es una solicitud, query es una consulta
    if request.method == "POST":
        usuario = personas.query.filter_by(apodo=request.form["username"]).first()
        passwords = personas.query.filter_by(password=request.form["password"]).first()

        #si usuario y el password del hash es igual al passwor del usuario return
        if usuario and passwords:
            return "Estas loggeado"
        return "tus credenciales son invalidas, revisa he intenta de nuevo "
    #si es de tipo GET que renderice la plantilla
    return render_template("login.html")

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,port=3000)
