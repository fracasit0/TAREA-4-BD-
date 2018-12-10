from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import make_response
from flask import session
from sqlalchemy import func
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
    id_c = db.Column(db.String(50), db.ForeignKey('cuenta.id'))

class cuenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Integer, nullable=False)
    gastado = db.Column(db.Integer, nullable=False)


class objeto(db.Model):
    nombre = db.Column(db.String(126))
    legalidad = db.Column(db.Boolean, nullable=False)
    codigo = db.Column(db.Integer, nullable=False, primary_key=True)
    precio = db.Column(db.Integer, nullable=False)
    dueno_act = db.Column(db.String(126), db.ForeignKey('personas.apodo'))

class policia(db.Model):
    placa = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(126), nullable=False)
    soborno = db.Column(db.String(126), nullable=False)
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


@app.route("/lugares")
def lugares():
    place = sector.query.all()
    return render_template("lugares.html", place = place)

@app.route("/usuarios")
def usuarios():
    user = personas.query.all()
    return render_template("usuarios.html", user = user)

@app.route("/objetos")
def objetos():
    object = objeto.query.all()
    return render_template("objetos.html", object = object)

@app.route("/addobject", methods=["GET"])
def addobject():
    if request.method == "GET":
            user = personas.query.all()
            return render_template("anadirobj.html", user = user)

@app.route("/addobject2", methods=["GET"])
def addobject2():
    if request.method == "GET":
            dueno = request.args.get("actual")
            user = personas.query.filter_by(apodo=dueno).first()
            legal = request.args.get("legal")
            if legal == None:
                legal = False
            else:
                legal = True
            if user:
                number = objeto.query.count()
                new_obj = objeto(nombre=request.args.get("name"), legalidad=legal, codigo=number+1, precio=request.args.get("price"), dueno_act=dueno)
                db.session.add(new_obj)
                db.session.commit()
                object = objeto.query.all()
                return render_template("objetos.html", object = object)
            return "El apodo de ese dueno no existe..."

@app.route("/addsec1")
def addsec1():
    return render_template("anadirsector.html")

@app.route("/addsec2", methods=["POST","GET"])
def addsec2():
    if request.method == "POST":
            encontrado = sector.query.filter_by(ubicacion = request.form["ubicacion"]).first()
            if encontrado == None:
                number = sector.query.count()
                new_sec = sector(numero=number+1, ubicacion=request.form["ubicacion"])
                db.session.add(new_sec)
                db.session.commit()
                place = sector.query.all()
                return render_template("lugares.html", place=place)
            return "La ubicacion del sector ya existe..."


@app.route("/addcop", methods=["POST","GET"])
def addcop():
    if request.method == "POST":
            encontrado = policia.query.filter_by(placa = request.form["placa_cop"]).first()
            if encontrado == None:
                new_cop = policia(placa=request.form["placa_cop"], nombre=request.form["name_cop"], soborno=request.form["soborno_cop"], num_s=request.form["sector_cop"])
                db.session.add(new_cop)
                db.session.commit()
                place = sector.query.all()
                return render_template("lugares.html", place = place)
            return "El numero de placa de este policia ya existe..."


@app.route("/search")
def search():
    nombre = request.args.get("buscar_user")
    user = personas.query.filter_by(apodo=nombre).first()
    object = objeto.query.filter_by(dueno_act=nombre).all()
    if user:
        return render_template("profile.html", user = user, object = object)

    else:
        return "El usuario no existe"

@app.route("/searchplaces", methods=["POST","GET"])
def searchplaces():
    if request.method == "GET":
        numero = request.args.get("Buscar_sec")
        place = sector.query.filter_by(numero=numero).first()
        police = policia.query.filter_by(num_s=numero).all()
        if place:
            return render_template("sector.html", place = place, police=police)

        else:
            return "El sector no existe"



@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method == "POST":

        #hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        number = cuenta.query.count()
        new_cuenta = cuenta(id=number+1, saldo=0, gastado=0)
        new_user = personas(apodo=request.form["username"], password=request.form["password"], nativo=request.form["native"], contacto=request.form["contact"], ventas=0, compras=0, id_c=number+1)

        db.session.add(new_user)
        db.session.add(new_cuenta)
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
            return render_template("profile.html", user = usuario, logeado = True)
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
    cuenta = cuenta(id=1, saldo=0, gastado=0)
    cuenta = sector(ubicacion="los heroes", numero=1)
    db.session.add(cuenta)
    db.session.add(sector)
