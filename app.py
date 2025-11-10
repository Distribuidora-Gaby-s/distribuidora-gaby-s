from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os

app = Flask(__name__)
app.secret_key = "distribuidora_gabys_2025"  # Clave para sesiones

BASE_DIR = os.path.join(os.path.dirname(__file__), "data")

# ---------------- FUNCIONES AUXILIARES ---------------- #
def cargar_json(nombre_archivo):
    ruta = os.path.join(BASE_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_json(nombre_archivo, data):
    ruta = os.path.join(BASE_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------------- RUTAS PRINCIPALES ---------------- #
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
                flash("Inicio de sesión exitoso ✅", "success")
                return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos ❌", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Has cerrado sesión correctamente 👋", "info")
    return redirect(url_for("login"))

# ---------------- CRUD PRODUCTOS ---------------- #
@app.route("/productos")
def productos():
    if "usuario" not in session:
        return redirect(url_for("login"))
    productos = cargar_json("productos.json")
    return render_template("productos.html", productos=productos)

@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            # log para depuración
            app.logger.info("POST nuevo_producto: %s", dict(request.form))

            productos = cargar_json("productos.json")
            nuevo = {
                "nombre": request.form.get("nombre","").strip(),
                "codigo": request.form.get("codigo","").strip(),
                "cantidad": int(request.form.get("cantidad", 0)),
                "precio": float(request.form.get("precio", 0))
            }

            # Validaciones básicas
            if not nuevo["nombre"] or not nuevo["codigo"]:
                flash("Nombre y código son obligatorios.", "warning")
                return redirect(url_for("nuevo_producto"))

            if any(p.get("codigo") == nuevo["codigo"] for p in productos):
                flash("Ya existe un producto con ese código ⚠️", "warning")
                return redirect(url_for("nuevo_producto"))

            productos.append(nuevo)
            guardar_json("productos.json", productos)
            flash("Producto registrado exitosamente ✅", "success")
            return redirect(url_for("productos"))
        except Exception as e:
            app.logger.error("Error al crear producto: %s\n%s", e, traceback.format_exc())
            flash("Ocurrió un error al registrar el producto.", "danger")
            return redirect(url_for("nuevo_producto"))

    # GET
    return render_template("nuevo_producto.html")

@app.route("/productos/editar/<codigo>", methods=["GET", "POST"])
def editar_producto(codigo):
    if "usuario" not in session:
        return redirect(url_for("login"))

    try:
        productos = cargar_json("productos.json")
    except Exception as e:
        app.logger.error("Error leyendo JSON en editar: %s", e)
        flash("Error leyendo datos.", "danger")
        return redirect(url_for("productos"))

    producto = next((p for p in productos if p.get("codigo") == codigo), None)
    if not producto:
        flash("Producto no encontrado ❌", "danger")
        return redirect(url_for("productos"))

    if request.method == "POST":
        try:
            app.logger.info("POST editar_producto %s: %s", codigo, dict(request.form))
            producto["nombre"] = request.form.get("nombre", producto.get("nombre")).strip()
            # no permitimos cambiar el código en el edit (si quieres permitirlo, habría que validar duplicados)
            producto["cantidad"] = int(request.form.get("cantidad", producto.get("cantidad", 0)))
            producto["precio"] = float(request.form.get("precio", producto.get("precio", 0)))
            guardar_json("productos.json", productos)
            flash("Producto actualizado correctamente ✅", "success")
            return redirect(url_for("productos"))
        except Exception as e:
            app.logger.error("Error actualizando producto: %s\n%s", e, traceback.format_exc())
            flash("Ocurrió un error al actualizar el producto.", "danger")
            return redirect(url_for("editar_producto", codigo=codigo))

    # GET
    return render_template("editar_producto.html", producto=producto)
    
@app.route("/productos/eliminar/<codigo>")
def eliminar_producto(codigo):
    if "usuario" not in session:
        return redirect(url_for("login"))

    productos = cargar_json("productos.json")
    productos = [p for p in productos if p["codigo"] != codigo]
    guardar_json("productos.json", productos)
    flash("Producto eliminado exitosamente 🗑️", "info")
    return redirect(url_for("productos"))

# ---------------- OTRAS SECCIONES ---------------- #
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

# ---------------- EJECUCIÓN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
