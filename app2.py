from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import make_response
from flask import session
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
#importo una biblioteca para los passwords y la seguridad

import os

dbdir= "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
app.config["SECRET_KEY"]= 'SECRETITA'
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
    apodo = db.Column(db.String(50), db.ForeignKey('personas.apodo'))


class objeto(db.Model):
    nombre = db.Column(db.String(126), primary_key=True)
    legalidad = db.Column(db.Boolean, nullable=False)
    codigo = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    duenos = db.Column(db.Integer, nullable=False)
    dueno_act = db.Column(db.String(50), db.ForeignKey('personas.apodo'))

class policia(db.Model):
    placa = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(126), nullable=False)
    soborno = db.Column(db.Date, nullable=False)
    num_s = db.Column(db.Integer, db.ForeignKey('sector.numero'))

class sector(db.Model):
    numero = db.Column(db.Integer, primary_key=True)
    ubicacion = db.Column(db.String(126), nullable=False)

def require_api_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        if 'api_session_token' not in session:
            return Response("Access denied")

        return func(*args, **kwargs)

    return check_token


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    nombre = request.args.get("nickname")
    user = personas.query.filter_by(apodo=nombre).first()
    if user:
        return render_template("profile.html", user = user)

    else:
        return "El usuario no existe"



@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method == "POST":

        #hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        new_user = personas(apodo=request.form["username"], password=request.form["password"], nativo=request.form["native"], contacto=request.form["contact"], ventas=0, compras=0)
        db.session.add(new_user)
        #nos confirma cadad uno de los cambios
        db.session.commit()
        return render_template("login.html")
    return  render_template("signup.html")

@app.route("/login",methods=["POST","GET"])
def login():
#request es una solicitud, query es una consulta
    if request.method == "POST":
        usuario = personas.query.filter_by(apodo=request.form["username"]).first()
        passwords = personas.query.filter_by(password=request.form["password"]).first()

        #si usuario y el password del hash es igual al passwor del usuario return
        if usuario and passwords:
            return render_template("profile.html", user = usuario, logeado = True, token = token)
        return "tus credenciales son invalidas, revisa he intenta de nuevo "
    #si es de tipo GET que renderice la plantilla
    return render_template("login.html")

@app.route("/profile/<apodo>", methods=['GET','POST'])
def profile(apodo):
    user = personas.query.filter_by(apodo=apodo).first()
    return render_template('profile.html', user=user)




if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,port=3000)
