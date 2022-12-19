import pandas as pd
import dhRepository as dhRep
from time import time
from dateutil.parser import parse as parseDate
from datetime import datetime
import dhLogs
import json
import re

import dhOperations as ops



import argparse

pattNumber = re.compile('-?[0-9]*,?[0-9]*\.*[0-9]*')





"""

    ini = time()
    df_reglas_higienizacion = pd.read_excel('configuracion.xlsx', sheet_name='RULES' )
    df_Archivos_Fuente      = pd.read_excel('configuracion.xlsx', sheet_name='SOURCE_FILES')
    df_Layouts              = pd.read_excel('configuracion.xlsx', sheet_name='LAYOUTS', dtype={'ALLOW_NULL':str})
    df_Reglas_Layouts       = pd.read_excel('configuracion.xlsx', sheet_name='RULE_LAYOUT')

    #df_Cat_Cluster          = pd.read_excel('Catalogos.xlsx', sheet_name='Clusters' )

    ConfDict = dict()
    ConfDict['df_Reglas_Higienizacion'] = df_reglas_higienizacion
    ConfDict['df_Archivos_Fuente'] = df_Archivos_Fuente
    ConfDict['df_Layouts'] = df_Layouts
    ConfDict['df_Cats'] = pd.read_excel('configuracion.xlsx', sheet_name='CATALOGS')

    print('Fuentes: {} \nReglas de higienización: {}\nColumnas de Layouts: {}'.format(
        len(df_Archivos_Fuente), len(df_reglas_higienizacion), len(df_Layouts) ))
    print ('Carga de Configuración = {} segundos'.format (time()-ini))


    print ('●●●●● CARGA DE CATALOGOS +++++++++++++++++++++++++++++++++++++++++++++++++')
    ini = time()
    CatDict = dict()
    dfCats = ConfDict['df_Cats']
    for ix, rw in dfCats.iterrows():
        CatDict[ rw['CAT_NAME'] ] = pd.read_excel( rw['CAT_FILE'] , sheet_name=rw['CAT_SHEET'] )
    print ('Carga de catalogos = {} segundos'.format (time()-ini))


    print ('●●●●● CARGA DE ARCHIVOS FUENTE +++++++++++++++++++++++++++++++++++++++++++')
    lsArchivosFuente = list()
    for ix, rw in df_Archivos_Fuente.iterrows():
        ini = time()
        if rw['SOURCE_TYPE'] == 'FILE_CSV' :
            df_Fuente = pd.read_csv(rw['SOURCE'])
        elif rw['SOURCE_TYPE'] == 'FILE_XLSX':
            df_Fuente = pd.read_excel(rw['SOURCE'], sheet_name=rw['PARAMS_READER'] )
        else:
            df_Fuente = pd.DataFrame()
        df_Fuente ['DQ_BITACORA_REGISTRO'] = ''
        lsArchivosFuente.append(df_Fuente)
        print('{} .- "{}" = {} segundos ( {} registros) '.format (
            ix+1,rw['SOURCE'], time() - ini,len(lsArchivosFuente[ix])))


    print ('●●●●● VALIDACION DE LAYOUTS +++++++++++++++++++++++++++++++++++++++++++')
    for ix, rw in df_Archivos_Fuente.iterrows():
        ini = time()
        print('{} .- "{}" '.format (ix+1, rw['SOURCE']))
        ValidarFormatoColumnas_Layout( lsArchivosFuente[ix], df_Layouts, rw['LAYOUT_NAME'])
        print('Tiempo de validación: {} segundos ( {} registros {} columnas) '.format (
            time() - ini, len(lsArchivosFuente[ix]), len( df_Layouts)))





    print ('●●●●● REGLAS DE HIGIENIZACION +++++++++++++++++++++++++++++++++++++++++')
    ini = time()
    Operaciones = 0
    for ix, rw in df_Archivos_Fuente.iterrows():
        dtf_rules = df_Reglas_Layouts[ df_Reglas_Layouts['LAYOUT_NAME'] == rw['LAYOUT_NAME']  ]
        for jx, grRule in dtf_rules.iterrows():
            AplicarSustitucionCaracteresAColumna (lsArchivosFuente[ix], df_reglas_higienizacion, grRule['COLUMN_NAME'], grRule['GROUP'] )
            Operaciones +=1

    print('Tiempo en Reglas de Higienización: {} segundos ( {} registros {} Regla(s) Aplicada(s) ) '.format (
            time() - ini, len(lsArchivosFuente[ix]), Operaciones ))



    print ('●●●●● VALIDACION DE CATALOGOS +++++++++++++++++++++++++++++++++++++++++')
    for ix, rw in df_Archivos_Fuente.iterrows():
        ini = time()
        df_cfg_catalogs =  df_Layouts.loc[ (df_Layouts['LAYOUT_NAME'] == rw[ 'LAYOUT_NAME' ]) & (df_Layouts['VALIDATION_CATALOG'].isna() == False )  ]
        ValidarValoresEnCatalogo (lsArchivosFuente[ix], df_cfg_catalogs, CatDict )
        print('Tiempo de validación Catalogos: {} segundos ( {} registros {} catalogos) '.format (
            time() - ini, len(lsArchivosFuente[ix]), len( df_cfg_catalogs)))


    print ('●●●●● ARCHIVOS DE SALIDA ++++++++++++++++++++++++++++++++++++++++++++++')
    for ix, rw in df_Archivos_Fuente.iterrows():
        ini = time()
        lsArchivosFuente[ix].to_csv( 'Salida' + str(ix) + '.csv' )
        print (lsArchivosFuente[ix])
        print('Tiempo de escritura de archivos de salida: {} segundos ( {} registros) '.format (
            time() - ini, len(lsArchivosFuente[ix])))

"""


def PerfilarDatos(dtFr_Dtos, ArchName):
    fout = open(ArchName, mode='w')

    fout.write(('<p>Número de registros:{}</p>').format(len(dtFr_Dtos)))
    fout.write(('<p>Número de Columnas:{}</p>').format(len(dtFr_Dtos.columns)))

    fout.write(('<table><tr>' + ('<td>{}</td>' * 4) + '</tr>').format(
        'Column_Name', 'Has NAN', 'Distinct Values', 'Sample Data'))

    for Col_Name in dtFr_Dtos.columns:
        Col_Values = dtFr_Dtos[Col_Name]
        distinct_Values = Col_Values.unique()
        has_nan = Col_Values.hasnans

        valores = str(distinct_Values[:3])
        valores = valores if len(valores) < 500 else '<<<Tamaño de dato excede espacio de vista previa>>>'
        valores = valores.replace('\n', '')

        fout.write(('<tr>' + ('<td>{}</td>' * 4) + '</tr>').format(
            Col_Name, has_nan, len(distinct_Values), valores))
    fout.write('</table>')
    fout.close()


def Convertir_ValorDelimitado_AColumnas(dtFr_Datos, NombreColumna, Delimitador):
    re_Delimitador = '\\' + Delimitador

    dtFr_Datos[NombreColumna + '_COUNT'] = f[NombreColumna].str.count(re_Delimitador) + 1
    nMaxSep = dtFr_Datos[NombreColumna + '_COUNT'].max() - 1

    dtFr_Datos[NombreColumna] += dtFr_Datos[NombreColumna + '_COUNT'].apply(lambda x: (nMaxSep - x + 1) * '|')
    ser_Valores = dtFr_Datos[NombreColumna].str.split(Delimitador)

    for nCol in range(0, nMaxSep + 1):
        newColName = NombreColumna + str(nCol)
        dtFr_Datos[newColName] = ser_Valores.apply(lambda s: s[nCol])
        dtFr_Datos[NombreColumna + '_LAST_LEVEL'] = dtFr_Datos.apply(
            lambda x: x[newColName] if x[newColName] != '' else x[NombreColumna + '_LAST_LEVEL'], axis=1)


def AplicarSustitucionCaracteresAColumna(dtFrDatos, dtFrReglas, nombre_columna, GrupoEscaneo):
    ### esta ya se pasó a operations
    resul = None
    gpoReglas = dtFrReglas[(dtFrReglas['GROUP'] == GrupoEscaneo) & (dtFrReglas['RULE_TYPE'] == 'SUST')]

    marcaBitacora = '[SUST_' + GrupoEscaneo + ':True]'

    for ix, Fila in gpoReglas.iterrows():
        valor_buscado = Fila['SCAN_VALUE']
        valor_remplazo = Fila['CHANGE_VALUE']

        resul = dtFrDatos[nombre_columna].str.contains(valor_buscado) if resul is None else dtFrDatos[
                                                                                                nombre_columna].str.contains(
            valor_buscado) & resul

        dtFrDatos[nombre_columna] = dtFrDatos[nombre_columna].str.replace(valor_buscado, valor_remplazo)

    dtFrDatos.loc[resul[resul == True].index, 'DQ_BITACORA_REGISTRO'] += marcaBitacora + ','


def ValidarRangodeValoresNumericos(dtFrDatos, dtFrReglas, nombre_columna, GrupoEscaneo):
    ### esta ya se pasó a operations
    gpoReglas = dtFrReglas[(dtFrReglas['GROUP'] == GrupoEscaneo)]  # & (dtFrReglas['RULE_TYPE']=='RANGE' ) ]
    marcaBitacora = '["{}":"{}"]'.format(nombre_columna, GrupoEscaneo)
    for ix, Fila in gpoReglas.iterrows():
        Minimo = Fila['MIN_VALUE']
        Maximo = Fila['MAX_VALUE']

        dtfNoValidos = dtFrDatos[((dtFrDatos[nombre_columna] < Minimo)
                                  | (dtFrDatos[nombre_columna] > Maximo)) & (
                                     ~dtFrDatos['DQ_BITACORA_REGISTRO'].str.contains(marcaBitacora))]
        dtFrDatos.loc[dtfNoValidos.index, 'DQ_BITACORA_REGISTRO'] += marcaBitacora + ','


def ValidarFecha(str):
    ### esta ya se pasó a operations
    try:
        if parseDate(str):
            return True
    except:
        return False


def ValidarFormatoObjeto(objeto, tipo, nulo):
    ### esta ya se pasó a operations
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
            elif re.fullmatch(pattNumber, objeto):
                return True;
        elif tipo == 'TEXT':
            return True;
    except:
        return False
    return False


def ValidarFormatoColumnas_Layout(dtFrDatos: pd.DataFrame, dtFrLayouts: pd.DataFrame, Layout_Name):
    ### esta ya se pasó a operations
    dtFrLayout = dtFrLayouts[dtFrLayouts['LAYOUT_NAME'] == Layout_Name]
    for ix, rw in dtFrLayout.iterrows():
        if rw['SOURCE_COLUMN_NAME'] not in dtFrDatos.columns:
            print('   Columna {} no existe en el archivo fuente'.format(rw['SOURCE_COLUMN_NAME']))

        print('\t** {}\t{}'.format(rw['SOURCE_COLUMN_NAME'], rw['ALLOW_NULL']))

        resul = dtFrDatos[rw['SOURCE_COLUMN_NAME']].apply(
            lambda cl: ValidarFormatoObjeto(cl, rw['SOURCE_DATA_TYPE'], rw['ALLOW_NULL']))

        if len(resul) > 0:
            resul = resul[resul == False]
            if len(resul) > 0:
                conj = set(dtFrDatos.loc[resul.index, rw['SOURCE_COLUMN_NAME']].fillna('(vacio)'))
                print(
                    '\t   Valores en la Columna {} no cumplen con el Formato {} >>> {}'.format(rw['SOURCE_COLUMN_NAME'],
                                                                                               rw['SOURCE_DATA_TYPE'],
                                                                                               conj))


def ValidarValoresEnCatalogo(dtFrDatos: pd.DataFrame, dtFrLayouts: pd.DataFrame, dictCats):
    ### esta ya se pasó a operations
    for ix, rw in dtFrLayouts.iterrows():
        cat = dictCats[rw['VALIDATION_CATALOG']]
        dtfNoValidos = dtFrDatos[rw['SOURCE_COLUMN_NAME']].isin(cat[rw['VALIDATION_COLUMN']])
        for ix, rw in dtFrDatos.iterrows():
            if rw['SOURCE_COLUMN_NAME'] not in dtFrDatos.columns:
                print('   Columna {} no existe en el archivo fuente'.format(rw['SOURCE_COLUMN_NAME']))
        dtFrDatos.loc[dtfNoValidos.index, 'DQ_BITACORA_REGISTRO'] += marcaBitacora + ','


def GenerarColumnaConCatalogo(dtFrDatos: pd.DataFrame, dtFrLayouts: pd.DataFrame, dictCats):
    ### esta ya se pasó a operations
    for ix, rw in dtFrLayouts.iterrows():
        cat = dictCats[rw['VALIDATION_CATALOG']]
        dtfNoValidos = dtFrDatos[rw['SOURCE_COLUMN_NAME']].isin(cat[rw['VALIDATION_COLUMN']])
        dtfNoValidos = dtfNoValidos[dtfNoValidos == False]
        marcaBitacora = '["{}":"{}"]'.format(rw['SOURCE_COLUMN_NAME'], rw['VALIDATION_COLUMN'])
        dtFrDatos.loc[dtfNoValidos.index, 'DQ_BITACORA_REGISTRO'] += marcaBitacora + ','



########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-pnm', '--project_name', required=True, help='Nombre del projecto donde se va a ejecutar el flujo')
    ap.add_argument('-sid', '--source_id', required=True,
                    help='objectid de la fuente sobre la que se ejecutará el flujo')
    ap.add_argument('-fid', '--flow_id', required=True, help='objectid del dataflow que se va a ejecutar')
    args = vars(ap.parse_args())
    print(args)

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
    dataflow = dhRep.BuscarDocumentoporId_Proyecto('DataFlows', args['flow_id'])
    if dataflow is None:
        print('ERROR: El dataflow especificado no existe, verifique su parámetro flow_id:' + args['flow_id'])
        exit(-1)
    else:
        print('Flujo a ejecutar: ' + dataflow['name'] + '...OK')

    #Diccionario que contiene a todos los datasources utilizados en el dataflow
    datasources = dict()
    
    # Se ejecutan todas las operaciones del flujo
    for step in dataflow['operations']:

        if step['operation'] in ops.__dict__:
            funcion = ops.__dict__[step['operation']]
            if callable(funcion):
                print('********************************************************** Operación ---> ' + step['operation'])
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

