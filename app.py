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
class Users(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    #unique me dice que el username es unico y nullable me dice que este no se ingresa vavio
    username = db.Column(db.String(50), unique= True, nullable=False)
    #ojo que no necesitamos que las claves sean unicas
    password = db.Column(db.String(80), nullable=False)

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/search")
def search():
    nickname = request.args.get("nickname")
    user = Users.query.filter_by(username=nickname).first()
    if user:
        return user.username

    return "El usuario no existe"

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        new_user = Users(username=request.form["username"], password=hashed_pw)
        db.session.add(new_user)
        #nos confirma cadad uno de los cambios
        db.session.commit()
        return "ya te has registrado exitosamente "
    return  render_template("signup.html")
@app.route("/login",methods=["GET","POST"])
def login():
#request es una solicitud, query es una consulta
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form["username"]).first()

        #si usuario y el password del hash es igual al passwor del usuario return
        if user and check_password_hash(user.password,request.form["password"]):
            return "Estas loggeado"
        return "tus credenciales son invalidas, revisa he intenta de nuevo "
    #si es de tipo GET que renderice la plantilla
    return render_template("login.html")

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,port=3000)
