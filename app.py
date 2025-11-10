from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os

app = Flask(__name__)
app.secret_key = "distribuidora_gabys_2025"  # Clave para sesiones

BASE_DIR = os.path.join(os.path.dirname(__file__), "data")

def cargar_json(nombre_archivo):
    ruta = os.path.join(BASE_DIR, nombre_archivo)
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    if "usuario" in session:
        return render_template("index.html", usuario=session["usuario"])
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuarios = cargar_json("usuarios.json")
        user = request.form["usuario"]
        pwd = request.form["password"]

        for u in usuarios:
            if u["usuario"] == user and u["password"] == pwd:
                session["usuario"] = user
                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Has cerrado sesión correctamente", "info")
    return redirect(url_for("login"))

@app.route("/productos")
def productos():
    if "usuario" not in session:
        return redirect(url_for("login"))
    productos = cargar_json("productos.json")
    return render_template("productos.html", productos=productos)

@app.route("/alertas")
def alertas():
    if "usuario" not in session:
        return redirect(url_for("login"))
    alertas = cargar_json("alertas.json")
    return render_template("alertas.html", alertas=alertas)

@app.route("/reportes")
def reportes():
    if "usuario" not in session:
        return redirect(url_for("login"))
    reportes = cargar_json("reportes.json")
    return render_template("reportes.html", reportes=reportes)

if __name__ == "__main__":
    app.run(debug=True)
