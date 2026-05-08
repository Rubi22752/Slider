import os
from flask import Flask, render_template, request, jsonify, session, redirect
#import mysql.connector
import base64
import psycopg2         <-- Versión para Postgres
app = Flask(__name__)
app.secret_key = 'clave_secreta_rubi'

# Configuración de base de datos
db_config = {
    'user': 'rhernandez',
    'password': 'rubi#2004',
    'host': '127.0.0.1',
    'database': 'slider_db'
}

def conectar_db():
    return mysql.connector.connect(**db_config)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/slider')
def slider_page():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('index.html')

@app.route('/verificar_login', methods=['POST'])
def verificar_login():
    datos = request.get_json()
    nombre = datos.get('nombre')
    email = datos.get('email')

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    query_busqueda = "SELECT * FROM usuarios WHERE nombre = %s AND email = %s"
    cursor.execute(query_busqueda, (nombre, email))
    usuario = cursor.fetchone()

    if usuario:
        session['usuario'] = nombre
        mensaje = "Bienvenido de nuevo"
    else:
        query_registro = "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)"
        cursor.execute(query_registro, (nombre, email))
        conexion.commit()
        session['usuario'] = nombre
        mensaje = "Usuario registrado y acceso concedido"

    cursor.close()
    conexion.close()
    return jsonify({"status": "success", "mensaje": mensaje})

@app.route('/obtener_imagenes')
def obtener_imagenes():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, imagen FROM galeria")
    fotos = cursor.fetchall()

    # Convertimos el binario de la DB a base64 para que el HTML lo entienda
    for foto in fotos:
        if foto['imagen']:
            foto['imagen'] = base64.b64encode(foto['imagen']).decode('utf-8')

    cursor.close()
    conexion.close()
    return jsonify(fotos)

@app.route('/agregar', methods=['POST'])
def agregar():
    try:
        nombre = request.form.get('nombre')
        file = request.files.get('imagen')
        
        if not file:
            return jsonify({"error": "No hay imagen"}), 400

        contenido_binario = file.read()

        conn = conectar_db()
        cursor = conn.cursor()
        sql = "INSERT INTO galeria (nombre, imagen) VALUES (%s, %s)"
        cursor.execute(sql, (nombre, contenido_binario))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_image', methods=['POST'])
def update_image():
    try:
        image_id = request.form.get('id')
        file = request.files.get('imagen')
        nombre_texto = request.form.get('nombre')

        if not file or not image_id:
            return jsonify({"error": "Faltan datos"}), 400

        contenido_binario = file.read()

        conn = conectar_db()
        cursor = conn.cursor()
        sql = "UPDATE galeria SET nombre = %s, imagen = %s WHERE id = %s"
        cursor.execute(sql, (nombre_texto, contenido_binario, image_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/borrar/<int:id>', methods=['DELETE'])
def borrar(id):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM galeria WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
