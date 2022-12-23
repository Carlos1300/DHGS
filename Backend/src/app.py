from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId, MongoClient
from flask_cors import CORS
from DHUtils import dhRepository, DatahubEx, dhOperations, dhLogs
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
def get_projects(email):
    
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
        "file_name": request.files['dataSource'].filename,
        "sheet_name": request.form['sheet']
    }
    
    if not add_project_request['name'] in MONGO_CLIENT.list_database_names():
        dhRepository.create_database(MONGO_CLIENT, add_project_request['name'])
    
    doc = dhRepository.BuscarRegistroEnBD('Projects', 'ProjectName', add_project_request['name'])
    if doc == None:
        new_project = MONGO_CLIENT['datahub']['Projects'].insert_one({
        "ProjectName": add_project_request['name'],
        "DataBaseName": add_project_request['name'],
        "User": email,
        "DateCreated": str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(datetime.now().year)
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

@app.route('/getDataPerf/<email>/<project>', methods=['GET'])
def get_data_perfs(email, project):
    data_perfs= MONGO_CLIENT[project]['DataPerf'].find_one({'name': 'Resume'})
    
    resume_cols = [data_perfs['schema']['fields'][x]['name'] for x in range(len(data_perfs['schema']['fields']))]
    resume_cols.remove('index')
    
    data_resume = []
    temp_dict = {}
    
    id = 1
    
    for col in resume_cols:
        temp_dict.update({'Column': col})
        temp_dict.update({'id': id})
        for i in range(len(data_perfs['data'])):
            temp_dict.update({str(data_perfs['data'][i]['index']) : data_perfs['data'][i][col]})
        dict_data = temp_dict.copy()
        data_resume.append(dict_data)
        id += 1
    
    return jsonify(data_resume)

@app.route('/getDataLoads/<email>/<project>', methods=['GET'])
def get_data_loads(email, project):
    
    loads = []
    
    id = 1
    
    
    for doc in MONGO_CLIENT[project]['DataSource_Loads'].find():
        loads.append({
            'id': id,
            '_id': str(ObjectId(doc['_id'])),
            'FileName': doc["FileName"],
            "SourceType": doc["SourceType"].upper(),
            "Status": doc["Status"],
            "Encoding": doc["Encoding"],
            "Rows": doc["CountRows"],
            "Columns": doc["CountColumns"]
        })
        
        
        id += 1
    
    return jsonify(loads)

####################################### DATA FLOW IMPLEMENTATION ###################################################

@app.route('/getRules', methods=['GET'])
def get_rules():
    
    rules = []
    
    id = 1
    
    
    for doc in MONGO_CLIENT['datahub']['Rules'].find():
        rules.append({
            'id': id,
            'name': doc["name"],
            "value": doc["value"],
            "desc": doc["description"],
            "params": doc["params"]
        })
        
        
        id += 1
    
    return jsonify(rules)

@app.route('/addFlow/<email>', methods=['POST'])
def add_flow(email):
    
    coming_json = request.get_json()
    flow_name = coming_json[0]['flowName']
    operations = coming_json[1:]
    
    new_flow = MONGO_CLIENT['datahub']['GeneralFlows'].insert_one({
        "Name": flow_name,
        "Operations": operations,
        "User": email,
        "DateCreated": str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(datetime.now().year)
    })
    
    return jsonify({"msg": "Jaló el back: " + str(ObjectId(new_flow.inserted_id))})

@app.route('/getGeneralFlows/<email>', methods=['GET'])
def get_gen_flows(email):
    
    flows = []
    
    id = 1
    
    
    for doc in MONGO_CLIENT['datahub']['GeneralFlows'].find({'User': email}):
        flows.append({
            'id': id,
            '_id': str(ObjectId(doc['_id'])),
            "FlowName": doc["Name"],
            "Operations": len(doc["Operations"]),
            "Sequence": doc["Operations"],
            "DateCreated": doc["DateCreated"]
        })
        
        
        id += 1
    
    return jsonify(flows)

@app.route('/getProjectFlows/<project>', methods=['GET'])
def get_project_flows(project):
    
    project_flows = []
    
    id = 1
    
    
    for doc in MONGO_CLIENT[project]['DataFlows'].find():
        project_flows.append({
            'id': id,
            '_id': str(ObjectId(doc['_id'])),
            "FlowName": doc["Name"],
            "Operations": len(doc["Operations"]),
            "Sequence": doc["Operations"],
            "DateCreated": doc["DateCreated"]
        })
        
        
        id += 1
    
    return jsonify(project_flows)

@app.route('/importFlow/<email>/<project>', methods=['POST'])
def import_flow(email, project):
    flow_id = request.get_json()
    
    flow = MONGO_CLIENT[project]['DataFlows'].find_one({'_id': ObjectId(flow_id), 'User': email})
    
    if flow == None:
        imported_flow = MONGO_CLIENT['datahub']['GeneralFlows'].find_one({'_id': ObjectId(flow_id), 'User': email})
        MONGO_CLIENT[project]['DataFlows'].insert_one(imported_flow)
        return jsonify({'msg': 'El flujo ha sido importado con éxito.' })
    
    else:
        return jsonify({'msg': 'El flujo ya se encuentra importado en este proyecto.'}), 401

@app.route('/applyFlow/<project>', methods=['POST'])
def apply_flow(project):
    flow_id = request.get_json()
    
    source_id = MONGO_CLIENT[project]['DataLoads'].find_one()['_id']
    
    args = {
        'project_name': project,
        'flow_id': flow_id,
        'source_id': source_id
    }
    
    # Se verifica que se haya especificado un proyecto válido
    bdProyecto = dhRepository.EstablecerBDProjecto(project)
    if bdProyecto is None:
        return jsonify({"msg": "No se encontró el nombre del proyecto " + project + " en el DataHub."}), 401
    else:
        print('Estableciendo BD Proyecto ...OK')

    # se verifica que exista el flujo especificado
    dataflow = dhRepository.BuscarDocumentoporId_Proyecto('DataFlows', flow_id)
    if dataflow is None:
        return jsonify({"msg": "No se encontró el flujo con id: " + flow_id + " en el DataHub."}), 401
    else:
        print('Flujo a ejecutar: ' + dataflow['Name'] + '...OK')

    #Diccionario que contiene a todos los datasources utilizados en el dataflow
    datasources = dict()
    
    # Se ejecutan todas las operaciones del flujo
    for step in dataflow['Operations']:

        if step['name'] in dhOperations.__dict__:
            funcion = dhOperations.__dict__[step['name']]
            if callable(funcion):
                print('********************************************************** Operación ---> ' + step['name'])
                ini = datetime.now()
                EjecucionCorrecta, resultado = funcion(datasources, args, step)
                fin = datetime.now()
                print('Tiempo de Ejecución: ' + str(fin - ini))
                if EjecucionCorrecta:
                    dhLogs.registrar_ejecucion_exitosa_operacion_dataflow_prj ( args['flow_id'], step )
                else:
                    print ('\nERROR:')
                    if 'execute_error_text' in step:
                        print(step['execute_error_text'])
                    dhLogs.registrar_ejecucion_fallida_operacion_dataflow_prj( args['flow_id'], step )
                    break
        else:
            print ('la operación no existe:' + step['operation'])
            step['execute_error_text'] = 'la operación no existe:' + step['operation']
            dhLogs.registrar_ejecucion_fallida_operacion_dataflow_prj(args['flow_id'], step)

    for val in datasources:
        print('---------------------------------------' + val + '---------------------------------------')
        print(datasources[val])

    return jsonify({'msg': "Back jalando"})
 

if __name__ == "__main__":
    app.run(debug=True)