from threading import local
from pymongo import MongoClient
from bson.objectid import ObjectId

"""
Archivo de Python encargado de ingresar a la base de datos de MongoDB así como establecer el proyecto en el que se trabajará. Igualmente,
contiene diversas funciones de búsqueda y manipulación de los valores contenidos en las colecciones de los proyectos.

"""


USUARIO = 'carav'
PASSWORD = 'avicar13'
SERVIDOR = 'localhost:27017'
DefaultBD = 'datahub'

local_mongo_client = MongoClient('mongodb://' + USUARIO + ':' + PASSWORD + '@' + SERVIDOR + '/' + DefaultBD)

db_Datahub = local_mongo_client[DefaultBD]
db_Proyecto = None

## CREACIÓN DE UNA FUNCIÓN PARA CONECTARSE A MONGO?


def BuscarRegistroEnBD(Coleccion, Llave, Valor, NombreBD=DefaultBD):
    
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


def Buscar_BaseDatos(NombreBaseDatos, NombreBD=DefaultBD):
    
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
