from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId
from flask_cors import CORS

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
## MONGO Connection
app.config['MONGO_URI']='mongodb://carav:avicar13@localhost:27017/datahub'
mongo = PyMongo(app)
## JWT
app.config["JWT_SECRET_KEY"] = "123456789"  # Cambiar antes de desplegar
jwt = JWTManager(app)

CORS(app)

db = mongo.db.users

@app.route('/users', methods=['POST'])
def createUser():
    new = db.insert_one({
        'name': request.json['name'],
        'email': request.json['email'],
        'password': request.json['password']
    })
    
    return jsonify(str(ObjectId(new.inserted_id)))

@app.route('/users', methods=['GET'])
def getUsers():
    users = []
    for doc in db.find():
        users.append({
            '_id': str(ObjectId(doc['_id'])),
            'name': doc["name"],
            "email": doc["email"],
            "password": doc["password"]
        })
    return jsonify(users)

@app.route('/users/<id>', methods=['GET'])
def getUser(id):
    user = db.find_one({'_id': ObjectId(id)})
    return jsonify({
        '_id': str(ObjectId(user['_id'])),
        'name': user["name"],
        "email": user["email"],
        "password": user["password"]
    })

@app.route('/users/<id>', methods=['DELETE'])
def deleteUser(id):
    db.delete_one({'_id': ObjectId(id)})
    return jsonify({'msg': 'Deleted'})

@app.route('/users/<id>', methods=['PUT'])
def updateUser(id):
    db.update_one({'_id': ObjectId(id)},{'$set':{
        'name': request.json['name'],
        'email': request.json['email'],
        'password': request.json['password']
    }})
    return jsonify({'mgs': 'Updated'})

@app.route("/", methods=["POST"])
def login():    
    email = request.json.get("email", None)
    
    user_info = db.find_one({'email': email})
    
    if user_info != None:
    
        if email == user_info['email']:
        
            password = request.json.get("password", None)
            
            if password == user_info['password']:
                
                access_token = create_access_token(identity=email)
                return jsonify(access_token=access_token)
            
            else:
                return jsonify({"msg": "Contraseña incorrecta"}), 401
        else:
            return jsonify({"msg": "Correo incorrecto"}), 401
    else:
        return jsonify({"msg": "Usuario no dado de alta"}), 401
    

if __name__ == "__main__":
    app.run(debug=True)