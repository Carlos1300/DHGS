import pandas as pd
from DHUtils import dhRepository as dhRep
from datetime import datetime
from DHUtils import dhUtilities
from DHUtils import dhLogs
import json
import pandas as pd

Proyecto = ''

#def BuscarRegistroCarga(argumentos):
#    doc = dhRep.BuscarDocumentoBDProyecto( 'DataSource_Loads', 'SourceName', FuenteDatos)
#    return doc

def RegistrarInicioCargaDeArchivo(argumentos):
    """
    Verifica que no se cargue un mismo archivo en dos ocasiones, a menos que se especifique que se trata de sobreescribir
    los datos existentes
    :param argumentos:
    :return: Devuelve un dict con los datos correpondientes al registro de carga creado o localizado
    """
    loaded_file = argumentos['file']
    
    if argumentos['source_type'] == 'xlsx':
        FuenteDatos = ':'.join([argumentos['file_name'] , argumentos['sheet_name']] )
    else:
        FuenteDatos = argumentos['file_name']

    doc = dhRep.BuscarDocumentoBDProyecto( 'DataSource_Loads', 'SourceName', FuenteDatos)
    if doc is None:
        doc = {
            'SourceName': FuenteDatos,
            'FileName': argumentos['file_name'],
            'SourceType': argumentos['source_type'],
            'Status': 'Creado',
            'Date_Begin': datetime.now()
        }

        if argumentos['source_type'] == 'xlsx':
            doc['SheetName']: argumentos['sheet_name']
        elif argumentos['source_type'] == 'csv':
            doc['Encoding'] = argumentos['encoding'] if argumentos['encoding'] else 'UTF-8'
            doc['Separator'] = argumentos['separator'] if argumentos['separator'] else ','


        dhRep.InsertarDocumentoBDProyecto('DataSource_Loads', doc)
        
        print('Registro Insertado')
    else:
        print('Registro localizado')
    
    return doc, loaded_file


def LeerHojaExcel_a_DataFrame (docLogCarga, doc_file):
    """
    Recibe un dict correspondiente a un registro de la coleccion 'DataSource_Loads' de donde se tomará los datos de la fuente de excel
    que debe ser cargada en un dataframe. Sobre ese mismo registro se actualizará el estatus de la carga
    :param docLogCarga: Diccionario que debe contener las llaves '_id', 'Filename', 'SheetName', y 'Status'
    :return: devuelve el dataframe cargado y el código de error (cero si la carga ocurre correctamente)
    """

    Archivo = docLogCarga['FileName']
    Hoja = docLogCarga['SheetName']
    IdCarga = docLogCarga['_id']

    # ### Se verifica que exista el archivo
    # ErrNumber = dhUtilities.VerificarExisteArchivo(Archivo)
    # if ErrNumber > 0:
    #     dhLogs.RegistrarError_BDProyecto('DataSource_Loads', IdCarga, ErrNumber, Archivo )
    #     return None, ErrNumber

    ### Se verifica que exista la hoja
    ErrNumber = dhUtilities.VerificarExisteHojaXlxs( Archivo, Hoja )
    if ErrNumber > 0:
        dhLogs.RegistrarError_BDProyecto('DataSource_Loads', IdCarga, ErrNumber, Archivo )
        return None, ErrNumber

    ### Se carga la hoja a memoria en un DataFrame
    df_Source = pd.read_excel(doc_file, Hoja)

    return  df_Source, 0


def LeerCsv_a_DataFrame (docCarga, doc_file):
    """
    Recibe un dict correspondiente a un registro de la coleccion 'DataSource_Loads' de donde se tomará los datos de la fuente de excel
    que debe ser cargada en un dataframe. Sobre ese mismo registro se actualizará el estatus de la carga
    :param docCarga: Diccionario que debe contener las llaves '_id', 'Filename', 'SheetName', y 'Status'
    :return: devuelve el dataframe cargado y el código de error (cero si la carga ocurre correctamente)
    """
    
    ### Se verifica que exista el archivo
    # ErrNumber = dhUtilities.VerificarExisteArchivo(docCarga['FileName'])
    # print(ErrNumber)
    # if ErrNumber > 0:
    #     dhLogs.RegistrarError_BDProyecto('DataSource_Loads', docCarga['_id'], ErrNumber, docCarga['FileName'] )
    #     return None, ErrNumber

    ### Se carga la hoja a memoria en un DataFrame
    df_Source = pd.read_csv(doc_file, encoding=docCarga['Encoding'], sep=docCarga['Separator'])

    return  df_Source, 0


def CargarFuente_a_Dataframe (argumentos):
    RegistroCarga, doc_file = RegistrarInicioCargaDeArchivo(argumentos)
    if argumentos['source_type'] == 'xlsx':
        df, err = LeerHojaExcel_a_DataFrame(RegistroCarga, doc_file)
    elif argumentos['source_type'] == 'csv':
        df, err = LeerCsv_a_DataFrame(RegistroCarga, doc_file)
    else:
        err = 1

    if err:
        RegistroCarga['Status'] = 'Error'
    else:
        RegistroCarga['Status'] = 'En Memoria'
        RegistroCarga['CountColumns'] = len ( df.columns )
        RegistroCarga['CountRows'] = len ( df )

    RegistroCarga['Date_End'] = datetime.now()

    dhRep.ActualizarAtributosdeDocumentoProyecto('DataSource_Loads', RegistroCarga, ['Status', 'Date_End'])

    return df, RegistroCarga

def Guardar_DataFrame_Fuente_BD(RegistroCarga, dtfr:pd.DataFrame):
    doc =  json.loads(dtfr.to_json(orient='table'))
    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    doc_perf = json.loads(dtfr.describe().to_json(orient='table'))
    doc['_id'] = RegistroCarga['_id']
    doc_perf['_id'] = RegistroCarga['_id']
    doc_perf['name'] = "Resume"
    dhRep.EliminarDocumentoProyecto ( 'DataLoads', doc)
    dhRep.InsertarDocumentoBDProyecto ( 'DataLoads', doc)
    dhRep.EliminarDocumentoProyecto ( 'DataPerf', doc_perf)
    dhRep.InsertarDocumentoBDProyecto ( 'DataPerf', doc_perf)




#
# ap = argparse.ArgumentParser()
# ap.add_argument('-pnm',    '--project_name', required=True, help='Nombre del projecto donde se va a cargar el archivo')
# ap.add_argument('-src',    '--source_type', required=True, help='Tipo de fuente a extraer (xlsx=Excel, csv=Delimitado, )')
#
# ap.add_argument('-fln',    '--file_name', required=False, help='Nombre del archivo fuente')
# ap.add_argument('-sht',    '--sheet_name', required=False, help='Nombre de la hoja del archivo fuente, aplica solo para archivos de Excel')
# ap.add_argument('-enc',    '--encoding', required=False, help='Codificación del archivo de texto ("UTF-8"(default),"ANSI", etc) , aplica solo para archivos de csv')
# ap.add_argument('-sep',    '--separator', required=False, help='Separador utilizado en el csv (","(default) ,"|", etc) , aplica solo para archivos de csv')
#
# args = vars(ap.parse_args())


# args = dhUtilities.validar_argumentos('DatahubEx')

# if all(value == None for value in args.values()):
#     exit(0)
# # Se busca y determina que exista el proyecto en la base de datos, si el proyecto no existe finaliza la ejecución
# dhRep.EstablecerBDProjecto(args['project_name'])
# if Proyecto is None:
#     print('ERROR: El proyecto especificado no existe :"{}"'.format(args['project_name']))
#     exit()


# df_Fuente,reg =  CargarFuente_a_Dataframe(args)
# Guardar_DataFrame_Fuente_BD(reg, df_Fuente)
# print('***** ID del archivo: ', end='')
# print(reg['_id'])