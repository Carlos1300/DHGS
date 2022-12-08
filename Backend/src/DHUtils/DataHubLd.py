from ast import arg
import pandas as pd
import dhRepository as dhRep
import csv
from time import time
from dateutil.parser import parse as parseDate
from datetime import datetime
import dhLogs
import json
import re
import dhOperations as ops
import argparse


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-pnm', '--project_name', required=True, help='Nombre del projecto donde se va a ejecutar el flujo')
    ap.add_argument('-sid', '--source_id', required=True,
                    help='objectid de la fuente sobre la que se ejecutará el flujo')
    ap.add_argument('-otp', '--output_type', required=True,
                    help='Tipo archivo a crear (xlsx=Excel, csv=Delimitado, )')
    ap.add_argument('-onm', '--output_name', required=True,
                    help='Nombre del archivo a crear )')
    args = vars(ap.parse_args())

    print('\n**************************************************************************************************************************')
    print('**************************************************************************************************************************')
    print('********************************************** Inicia ejecución del datahub **********************************************')
    print('**************************************************************************************************************************')
    print('**************************************************************************************************************************')


    # Se verifica que se haya especificado un proyecto válido
    bdProyecto = dhRep.EstablecerBDProjecto(args['project_name'])
    if bdProyecto is None:
        print('ERROR: El proyecto Especificado no existe, verifique su parámetro : -pnm')
        exit(-1)
    else:
        print('Estableciendo BD Proyecto ...OK')

    # se verifica que exista el flujo especificado
    cleaned = dhRep.BuscarDocumentoporId_Proyecto('DataCleaned', args['source_id'])
    if cleaned is None:
        print('ERROR: La fuente especificada no existe, verifique su parámetro source_id:' + args['source_id'])
        exit(-1)

    #Diccionario que contiene a todos los datasources utilizados en el dataflow
    datasources = dict()

    dictObj = dhRep.obtener_atributos_por_docid_prj('DataCleaned', args['source_id'], ['schema','data'] )
    dtfrm = pd.read_json(json.dumps(dictObj), orient='table')

    if args['output_type'] == 'xlsx':
        name = args['output_name'] + '.xlsx'
        dtfrm.to_excel(name, 'Hoja1')
    elif args['output_type'] == 'csv':
        name = args['output_name'] + '.csv'
        dtfrm.to_csv(name,quotechar='"', quoting=csv.QUOTE_ALL )

    else:
        print('Formato de archivo de salida no soportado:{}'.format(args['output_type']))