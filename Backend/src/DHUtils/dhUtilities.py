from os import path
# from xlrd import open_workbook
import  sys
import pandas as pd
import re
from dateutil.parser import parse as parseDate
import argparse
import json
import numpy as np

pattNumber = re.compile('-?[0-9]*,?[0-9]*\.*[0-9]*')


def get_byte_size(df, encoding):

    doc = json.loads(df.to_json(orient='table'))
    byte_size = len(json.dumps(doc).encode(encoding))
    return byte_size

def chunk_partitioning(byte_size, df, MONGO_BYTES = 16793598):

    chunks = 2
    
    while byte_size > MONGO_BYTES:
        operation = round(byte_size / chunks)
        
        if operation < MONGO_BYTES:
            break
        
        chunks = chunks * 2

    df_chunks = np.array_split(df, chunks)

    return df_chunks

def chunk_partitioning_save(df, chunks):
    df_chunks = np.array_split(df, chunks)
    return df_chunks

# def VerificarExisteArchivo (FilePath):
#     if path.isfile(FilePath):
#         return 0
#     return 100 #ERRORCODENUMBER: archivo no existente

# def VerificarExisteHojaXlxs (Archivo, Hoja):
#     xlsx = open_workbook(Archivo)
#     ExisteHoja = Hoja in xlsx.sheet_names()
#     xlsx.release_resources()
#     if ExisteHoja:
#         return 0
#     return 101 #ERRORCODENUMBER: de archivo no existente

def ValidarFecha(str):
    try:
        if parseDate(str):
            return True
    except:
        return False

def ValidarFormatoObjeto(objeto, tipo, nulo):
    try:
        if isinstance(objeto, float) and pd.isna(objeto):
            if nulo == 'TRUE':
                return True
            else:
                return False
        elif tipo == 'DIGITS':
            if (str.isdigit(objeto)): return True;
        elif tipo == 'ALPHANUM':
            cad = str.isalnum(objeto)
            if cad and objeto != 'nan': return True;
        elif tipo == 'DATE':
            if parseDate(objeto): return True;
        elif tipo == 'NUMBER':
            if isinstance(objeto, float):
                return True;
            elif re.fullmatch(pattNumber, str(objeto)):
                return True;
        elif tipo == 'TEXT':
            return True;
    except:
        print('***' + str(sys.exc_info()))
        return False
    return False


def validar_argumentos(scriptname):
    """
    Verifica que los argumentos enviados desde línea de comandos para cada script sean los correctos
    :param scriptname: Nombre del script de Datahub que esta siendo ejecutado
    :return: Devuelve un dict con todos los argumentos cargados
    """

    parametrosRequeridos = list()

    ap = argparse.ArgumentParser()

    #El nombre del proyecto, todos los comandos de datahub se ejecutan dentro del contexto de un proyecto
    ap.add_argument('-pnm', '--project_name', required=False,help='Nombre del projecto donde se va a cargar el archivo')
    parametrosRequeridos.append('pnm')

    # Script de Extracción
    if scriptname == 'DatahubEx':
        #Tipo de archivo que se va a cargar
        ap.add_argument('-src', '--source_type',  required=False,help='Tipo de fuente a extraer (xlsx=Excel, csv=Delimitado, )')
        parametrosRequeridos.append('src')

        #Para archivos csv, xls, xlsx
        ap.add_argument('-fln', '--file_name', required=False, help='Nombre del archivo fuente que incluye la ruta')

        #Para archivos de Excel: xls, xlsx
        ap.add_argument('-sht', '--sheet_name', required=False,help='Nombre de la hoja del archivo fuente, aplica solo para archivos de Excel')

        #Para archivos csv
        ap.add_argument('-enc', '--encoding', required=False,help='Codificación del archivo de texto ("UTF-8"(default),"ANSI", etc) , aplica solo para archivos de csv')
        ap.add_argument('-sep', '--separator', required=False,help='Separador utilizado en el csv (","(default) ,"|", etc) , aplica solo para archivos de csv')

        args = vars(ap.parse_args())
        return args

    # Transformación
    # ap.add_argument('-pnm', '--project_name', required=True, help='Nombre del projecto donde se va a ejecutar el flujo')
   # ap.add_argument('-sid', '--source_id', required=False,help='objectid de la fuente sobre la que se ejecutará el flujo')
    #ap.add_argument('-fid', '--flow_id', required=True, help='objectid del dataflow que se va a ejecutar')

    #args = vars(ap.parse_args())




    #return argumentos_dict
