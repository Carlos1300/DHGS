from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId, MongoClient
from flask_cors import CORS
from DHUtils import dhRepository, DatahubEx
import pandas as pd
from datetime import datetime

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

import json

app = Flask(__name__)

## MONGO Connection
app.config['MONGO_URI']='mongodb://carav:avicar13@localhost:27017'
mongo = PyMongo(app)
MONGO_CLIENT = MongoClient('mongodb://carav:avicar13@localhost:27017')


## JWT
app.config["JWT_SECRET_KEY"] = "123456789"  # Cambiar antes de desplegar
jwt = JWTManager(app)

CORS(app)

@app.route('/users', methods=['POST'])
def createUser():
    new = mongo.db.users.insert_one({
        'name': request.json['name'],
        'email': request.json['email'],
        'password': request.json['password']
    })
    
    return jsonify(str(ObjectId(new.inserted_id)))

@app.route('/users', methods=['GET'])
def getUsers():
    users = []
    for doc in mongo.db.users.find():
        users.append({
            '_id': str(ObjectId(doc['_id'])),
            'name': doc["name"],
            "email": doc["email"],
            "password": doc["password"]
        })
    return jsonify(users)

@app.route('/users/<id>', methods=['GET'])
def getUser(id):
    user = mongo.db.users.find_one({'_id': ObjectId(id)})
    return jsonify({
        '_id': str(ObjectId(user['_id'])),
        'name': user["name"],
        "email": user["email"],
        "password": user["password"]
    })

@app.route('/users/<id>', methods=['DELETE'])
def deleteUser(id):
    mongo.db.users.delete_one({'_id': ObjectId(id)})
    return jsonify({'msg': 'Deleted'})

@app.route('/users/<id>', methods=['PUT'])
def updateUser(id):
    mongo.db.users.update_one({'_id': ObjectId(id)},{'$set':{
        'name': request.json['name'],
        'email': request.json['email'],
        'password': request.json['password']
    }})
    return jsonify({'mgs': 'Updated'})


############################### DATAHUB ###########################################

# ACTIVE_PROJECT_DB = None

@app.route("/", methods=["POST"])
def login():   
    email = request.json.get("email", None)
    
    user_info = MONGO_CLIENT['datahub']['users'].find_one({'email': email})
    
    if user_info != None:
    
        if email == user_info['email']:
        
            password = request.json.get("password", None)
            
            if password == user_info['password']:
                
                access_token = create_access_token(identity=email)
                return jsonify({
                    "name": user_info['name'],
                    "address": user_info['address'],
                    "country": user_info['country'],
                    "email": user_info['email'],
                    "tel": user_info['tel'],
                    "token": access_token
                    })
            
            else:
                return jsonify({"msg": "Contraseña incorrecta"}), 401
        else:
            return jsonify({"msg": "Correo incorrecto"}), 401
    else:
        return jsonify({"msg": "Usuario no dado de alta"}), 401
    
    
@app.route('/getProjects/<email>', methods=['GET'])
def getProjects(email):
    
    projects = []
    
    id = 1
    
    
    for doc in MONGO_CLIENT['datahub']['Projects'].find({'User': email}):
        projects.append({
            'id': id,
            '_id': str(ObjectId(doc['_id'])),
            'ProjectName': doc["ProjectName"],
            "DataBaseName": doc["DataBaseName"],
            "DateCreated": doc["DateCreated"]
        })
        
        
        id += 1
    
    return jsonify(projects)


@app.route('/addProject/<email>', methods=['POST'])
def add_project(email):
    add_project_request = {
        "file": request.files['dataSource'],
        "name": request.form['pName'],
        "source_type": request.form['fileType'],
        "separator": request.form['sep'],
        "encoding": request.form['enc'],
        "file_name": request.files['dataSource'].filename
    }
    
    if not add_project_request['name'] in MONGO_CLIENT.list_database_names():
        dhRepository.create_database(MONGO_CLIENT, add_project_request['name'])
        print('Se ha creado la base de datos')
    
    doc = dhRepository.BuscarRegistroEnBD('Projects', 'ProjectName', add_project_request['name'])
    if doc == None:
        new_project = MONGO_CLIENT['datahub']['Projects'].insert_one({
        "ProjectName": add_project_request['name'],
        "DataBaseName": add_project_request['name'],
        "User": email,
        "DateCreated": str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(datetime.now().year) + ' - ' + str(datetime.now().hour) + ':' + str(datetime.now().minute)
        })
        
        msg = 'Se ha agregado con éxito la fuente de datos con el ID de objeto'
        project_id = str(ObjectId(new_project.inserted_id))
    
    else:
        msg = 'Se ha actualizado con éxito la fuente de datos con el ID de objeto'
        project_id = str(doc['_id'])
        
    dhRepository.EstablecerBDProjecto(add_project_request['name'])
    df_Fuente, reg =  DatahubEx.CargarFuente_a_Dataframe(add_project_request)
    DatahubEx.Guardar_DataFrame_Fuente_BD(reg, df_Fuente)
    
    return jsonify({
        'msg': msg,
        'objID': project_id
        })
    
@app.route('/method', methods=['POST'])
def applyMethod():
    
    p = []
    
    methods = request.json.get('methods', None)
    for method in methods:
        print("The Method is: %s" % (method))
        for param in methods[method]['params']:
            p.append(methods[method]['params'][param])
        print(p)
    return jsonify(methods)
 

if __name__ == "__main__":
    app.run(debug=True)