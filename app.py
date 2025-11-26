from flask import Flask, render_template, request, redirect, url_for, flash
import json, os

app = Flask(__name__)
app.secret_key = "distribuidora_gabys_2025"

BASE_DIR = os.path.join(os.path.dirname(__file__), "data")

# ------------------------------
# Funciones auxiliares
# ------------------------------

def cargar_json(nombre_archivo):
    ruta = os.path.join(BASE_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_json(nombre_archivo, data):
    ruta = os.path.join(BASE_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ------------------------------
# Registrar Producto
# ------------------------------

@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    tipos = ["aseo personal", "hogar", "otros"]

    if request.method == "POST":
        productos = cargar_json("productos.json")

        nuevo = {
            "nombre": request.form["nombre"],
            "codigo": request.form["codigo"],
            "cantidad": int(request.form["cantidad"]),
            "precio": float(request.form["precio"]),
            "tipo": request.form["tipo"]
        }

        # Validación de código repetido
        if any(p["codigo"] == nuevo["codigo"] for p in productos):
            flash("Ya existe un producto con ese código.", "danger")
            return redirect(url_for("nuevo_producto"))

        productos.append(nuevo)
        guardar_json("productos.json", productos)
        flash("Producto agregado correctamente.", "success")
        return redirect(url_for("nuevo_producto"))

    return render_template("nuevo_producto.html", tipos=tipos)

# ------------------------------
# Ejecutar aplicación
# ------------------------------

if __name__ == "__main__":
    app.run(debug=True)
