from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
import logging
 
app = Flask(__name__)

# Clé pour signer token
app.config["JWT_SECRET_KEY"] = "ma_cle_secrete"
jwt = JWTManager(app)

# Configuration pour logger
logging.basicConfig(
    filename="crud.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)
@app.before_request
def log():
    remote_addr = request.remote_addr
    remote_url = request.url
    remote_method = request.method
    logging.info("Connexion depuis IP " + remote_addr + " a l'url " + remote_url + " selon la methode " + remote_method)    
 
# Données non stockée
users = [
    {"id": 1, "nom": "Alice", "email": "alice@example.com", "password": "1234", "role":"admin"},
    {"id": 2, "nom": "Bob",   "email": "bob@example.com", "password": "1234", "role":"user"},
]
next_id = 3

# Route pour obtenir jeton JWT avec rôle selon utilisateur
@app.route("/login", methods=["POST"])
def identifiant():
    data = request.get_json()
    for user in users:
        if user["nom"] == data["nom"] and user["password"] == data["password"]:
            access_token = create_access_token(identity=data["nom"], additional_claims={"role":user["role"]})
    return(jsonify({"token" : access_token}))
                        
    
# Méthode GET
@app.route("/users")
def get_users():
    return jsonify(users)

@app.route("/users/<int:id>")
def get_user(id):
    return jsonify(users[id-1])

@app.route("/log")
@jwt_required()
def read_log():
    claims = get_jwt()
    role = claims["role"]
    if role != "admin":
        return jsonify({"erreur": "Pas assez de privilèges"}), 403
    with open("crud.log", "r", encoding="cp1252") as file:
        return file.read(), 200, {"Content-Type": "text/plain; charset=utf-8"}
        

# Méthode POST protéger avec JWT + vérification rôle (seule admin peuvent crée)
@app.route("/users", methods=["POST"])
@jwt_required()
def new_user():
    claims = get_jwt()
    role = claims["role"]
    if role != "admin":
        return jsonify({"erreur": "Pas assez de privilèges"}), 403
        
    global next_id
    data = request.get_json()
    info = {"id": next_id, "nom": data["nom"], "email": data["email"], "password": data["password"]}
    users.append(info)
    next_id += 1
    return jsonify(info)

# Méthode PUT
@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    for user in users:
        if user["id"] == id:
            data = request.get_json()
            user["nom"] = data["nom"]
            user["email"] = data["email"]
            return jsonify(user)

# Méthode DELETE    
@app.route("/users/<int:id>", methods=["DELETE"])
def erase_user(id):
    for user in users:
        if user["id"] == id:
            users.remove(user)
            return jsonify({"message": "User " + str(id) + " supprimé"}), 200

# Lancer Flask
app.run(debug=True, ssl_context='adhoc')