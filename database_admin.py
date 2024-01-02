from flask import Flask, request, jsonify
import sqlite3
import jwt
import hashlib
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) 
app.config['SECRET_KEY'] = 'super-secreto'  


conn = sqlite3.connect('usuarios.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT, 
              password TEXT, 
              nombre TEXT,               
              correo TEXT, 
              direccion TEXT)''')
conn.commit()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = str(data['username'])
    password = str(data['password'])
    nombre = str(data['nombre'])    
    correo = str(data['correo'])
    direccion = str(data['direccion'])

    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (username, password, nombre, correo, direccion) VALUES (?, ?, ?, ?, ?)", 
              (username, password, nombre,  correo, direccion))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Usuario registrado exitosamente'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if user and user[2] == password:
        token = jwt.encode({'username': username}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify(access_token=token)
    return jsonify({'message': 'Nombre de usuario o contraseña incorrectos....'}), 401

@app.route('/verificar-token', methods=['POST'])
def verificar_token():
    token = request.headers.get('Authorization').split(" ")[1]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'message': 'Token válido'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token inválido'}), 401
        

@app.route('/obtener-datos-usuario', methods=['GET'])
def obtener_datos_usuario():
    token = request.headers.get('Authorization').split(" ")[1]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        username = data['username']
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        c.execute("SELECT nombre, correo, direccion FROM usuarios WHERE username=?", (username,))
        user_data = c.fetchone()
        conn.close()
        if user_data:
            nombre, correo, direccion = user_data
            return jsonify({'username': username, 'nombre': nombre, 'correo': correo, 'direccion': direccion}), 200
        else:
            return jsonify({'message': 'Información del usuario no encontrada'}), 404
    except Exception as ex:
        print(ex)
        return jsonify({'message': 'Error al obtener información del usuario'}), 401
                
if __name__ == '__main__':
    app.run(debug=True)