from threading import local
from pymongo import MongoClient
from bson.objectid import ObjectId
from io import StringIO
import json
import pandas as pd

"""
Archivo de Python encargado de ingresar a la base de datos de MongoDB así como establecer el proyecto en el que se trabajará. Igualmente,
contiene diversas funciones de búsqueda y manipulación de los valores contenidos en las colecciones de los proyectos.

"""


USUARIO = 'carav'
PASSWORD = 'avicar13'
SERVIDOR = 'localhost:27017'
# DefaultBD = 'datahub'

local_mongo_client = MongoClient('mongodb://' + USUARIO + ':' + PASSWORD + '@' + SERVIDOR)

db_Datahub = local_mongo_client['datahub']
db_Proyecto = None

## CREACIÓN DE UNA FUNCIÓN PARA CONECTARSE A MONGO?


def BuscarRegistroEnBD(Coleccion, Llave, Valor, NombreBD='datahub'):
    
    """
    Función encargada de buscar y encontrar el primer valor que se encuentre y que
    sea igual a la consulta que se haga.

    Argumentos:
            Coleccion (str) un string que corresponde a la colección a la que se accederá.
            Llave (str) un string que corresponde al nombre del registro que buscamos.
            Valor (str) un string que nos indica el valor que se está buscando.
            NombreBD (str) que nos indica la base de datos a la que se conectará la persona.
            
    Regresa:
            doc un diccionario conteniendo el primer resultado que se encontró que concuerda
            con la consulta que se hizo.
    """
    
    doc = local_mongo_client[NombreBD][Coleccion].find_one({Llave: Valor})
    return doc

def BuscarCatalogoEnBD(Coleccion, Llave, Valor, NombreBD='datahub'):
    
    """
    Función encargada de buscar y encontrar el primer valor que se encuentre y que
    sea igual a la consulta que se haga.

    Argumentos:
            Coleccion (str) un string que corresponde a la colección a la que se accederá.
            Llave (str) un string que corresponde al nombre del registro que buscamos.
            Valor (str) un string que nos indica el valor que se está buscando.
            NombreBD (str) que nos indica la base de datos a la que se conectará la persona.
            
    Regresa:
            doc un diccionario conteniendo el primer resultado que se encontró que concuerda
            con la consulta que se hizo.
    """
    
    doc = local_mongo_client[NombreBD][Coleccion].find_one({Llave: Valor}, {'_id': 0, 'data': 1, 'schema': 1})
    return doc


def BuscarDocumentoBDProyecto(Coleccion, Llave, Valor):
    
    """
    Función encargada de buscar y encontrar el primer valor que se encuentre y que
    sea igual a la consulta que se haga en el proyecto seleccionado.

    Argumentos:
            Coleccion (str) un string que corresponde a la colección a la que se accederá.
            Llave (str) un string que corresponde al nombre del registro que buscamos.
            Valor (str) un string que nos indica el valor que se está buscando.
            
    Regresa:
            doc un diccionario conteniendo el primer resultado que se encontró que concuerda
            con la consulta que se hizo dentro del proyecto seleccionado.
    """
    
    doc = db_Proyecto[Coleccion].find_one({ Llave : Valor })
    return doc


def BuscarDocumentoporId_Proyecto(Coleccion, idDoc):
    
    """
    Función encargada de buscar y encontrar el primer valor que se encuentre y que
    sea igual al ID generado por MongoDB.

    Argumentos:
            Coleccion (str) un string que corresponde a la colección a la que se accederá.
            idDoc (str) un string que contiene el id del objeto generado por MongoDB.
            
    Regresa:
            doc un diccionario conteniendo el primer resultado que se encontró que concuerda
            con el ID dentro del proyecto seleccionado.
    """
    
    # print(Coleccion)
    # print(idDoc)
    doc = db_Proyecto[Coleccion].find_one({'_id': ObjectId(idDoc) })
    return doc


def InsertarDocumentoBDProyecto(Coleccion, Documento):
    
    """
    Función encargada de insertar un nuevo registro a la base de datos del proyecto
    seleccionado.

    Argumentos:
            Coleccion (str) un string que corresponde a la colección a la que se accederá.
            Documento (dict) un dictionary que contiene los valores del registro que se
            agregará.
            
    Regresa:
            doc un dictionary que contiene el nuevo objeto que se agregó.
    """
    
    nuevo = db_Proyecto[Coleccion].insert_one(Documento)
    doc = db_Proyecto[Coleccion].find_one({'_id': nuevo.inserted_id})
    return doc

def insert_document_db(collection, doc, DB = 'datahub'):
    new = local_mongo_client[DB][collection].insert_one(doc)
    doc = local_mongo_client[DB][collection].find_one({'_id': new.inserted_id})
    return doc


def Buscar_BaseDatos(NombreBaseDatos):
    
    """
    Función encargada de informar si una base de datos se encuentra en el servidor.

    Argumentos:
            NombreBaseDatos (str) un string que contiene el nombre de la base de
            datos que se buscará en el servidor.
            
    Regresa:
            True si la base de datos se encuentra indexada.
            False si no se encontró la base de datos.
    """
    
    return (NombreBaseDatos in local_mongo_client.list_database_names())


def EstablecerBDProjecto(NombreProyecto):
    
    """
    Función encargada de seleccionar el proyecto con el que se va a trabajar.

    Argumentos:
            NombreProyecto (str) un string que contiene el nombre del proyecto.
            que se buscará en la colección Projects de la base de datos principal.
            
    Regresa:
            Un objeto Database de MongoDB que nos indica que estamos conectados a la
            base de datos que corresponde al proyecto seleccionado.
            
    """
    
    global db_Proyecto #Se especifica usar la variable global db_Proyecto
    doc = db_Datahub['Projects'].find_one({'ProjectName': NombreProyecto})
    db_Proyecto = local_mongo_client[doc['DataBaseName']] \
        if doc['DataBaseName'] in local_mongo_client.list_database_names() else None
    return db_Proyecto



def ActualizarAtributosdeDocumentoProyecto(Coleccion, Documento, Campos=None):      #### PREGUNTAR SI SE PUEDE QUITAR LA VARIABLE CAMPOS
    
    """
    Función encargada de actualizar un registro en una colección perteneciente a la
    base de datos del proyecto.

    Argumentos:
            Coleccion (str) un string que contiene la colección almacenada en la base
            de datos del proyecto.
            Documento (dict) un dictionary que contiene la información que se va a
            actualizar en la colección.
            
    Regresa:
            ???
            
    """
    
    db_Proyecto[Coleccion].update_one( {'_id' : Documento['_id'] }, {'$set': Documento } )


def EliminarDocumentoProyecto(Coleccion, Documento):
    
    """
    Función encargada de eliminar un registro en una colección perteneciente a la
    base de datos del proyecto.

    Argumentos:
            Coleccion (str) un string que contiene la colección almacenada en la base
            de datos del proyecto.
            Documento (dict) un dictionary que contiene el id del registro que va a
            ser eliminado en la colección.
            
    Regresa:
            ???
            
    """
    
    db_Proyecto[Coleccion].delete_one( {'_id' : Documento['_id'] } )

    
def obtener_atributos_por_docid_prj(Coleccion, idDoc, Campos_List):
    """
    Busca en la Colección indicada, con base al idDoc y devuelve los Campos
    :param Coleccion: string
    :param idDoc: string
    :param idDoc: list of strings con los nombres de los campos
    :return: Documento (dict) con los Campos especificados
    """

    campos_dict = { name : 1 for name in Campos_List  }

    if '_id' not in Campos_List:
        campos_dict['_id'] = 0

    doc = db_Proyecto[Coleccion].find_one({'_id': ObjectId(idDoc)}, campos_dict)

    return doc

def obtener_atributos_prj_many(Coleccion, Campos_List):
    """
    Busca en la Colección indicada, con base al idDoc y devuelve los Campos
    :param Coleccion: string
    :param idDoc: string
    :param idDoc: list of strings con los nombres de los campos
    :return: Documento (dict) con los Campos especificados
    """

    campos_dict = { name : 1 for name in Campos_List  }

    if '_id' not in Campos_List:
        campos_dict['_id'] = 0

    complete_doc = []
    doc = db_Proyecto[Coleccion].find({}, campos_dict)
    
    for reg in doc:
        complete_doc.append(reg)
    

    return complete_doc

def obtener_atributos_por_filtro_prj(Coleccion, filtroDict, Campos_List):
    """
    Busca en la Colección indicada, con base al filtro indicado y devuelve los Campos
    :param Coleccion: string
    :param idDoc: string
    :param idDoc: list of strings con los nombres de los campos
    :return: Documento (dict) con los Campos especificados
    """

    campos_dict = { name : 1 for name in Campos_List }
    
    if '_id' not in Campos_List:
        campos_dict['_id'] = 0
    
    docs = db_Proyecto[Coleccion].find(filtroDict , campos_dict)

    return docs

######################### DATAHUB BACKEND REST API ###################################

def create_database(client, project):
        new_db = client[project]
        new_db['DataFlows'].insert_one({"test": 'test'})
        new_db['DataCleaned'].insert_one({"test": 'test'})

        new_db['DataFlows'].delete_one({"test": 'test'})
        new_db['DataCleaned'].delete_one({"test": 'test'})
        
        return True

def register_count(collection):
        
        count = db_Proyecto[collection].count_documents({})
        return count

def join_chunk_data(collection):
        full_df = None
        first = True

        for doc in db_Proyecto[collection].find({}, {'_id' : 0, 'schema': 1, 'data' : 1}):
                if first == True:
                        full_df = pd.read_json(StringIO(json.dumps(doc)), orient='table')
                        first = False
                else:
                        df_loaded_chunk = pd.read_json(StringIO(json.dumps(doc)), orient='table')
                        full_df = pd.concat([full_df, df_loaded_chunk])
        return full_df

def delete_chunk_data(collection):
        db_Proyecto[collection].delete_many({})
        return True