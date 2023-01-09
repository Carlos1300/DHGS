from ast import main
from numpy import AxisError, DataSource
from pandas.core.frame import DataFrame
from DHUtils import dhRepository as dhRep
import json
import pandas as pd
from DHUtils import dhLogs as log
from bson.objectid import ObjectId
from openpyxl.workbook import Workbook
from io import StringIO
from DHUtils import dhUtilities
from itertools import repeat
import html
import re
import numpy as np
import jellyfish
import operator
import unidecode
from datetime import date
import datetime
import openpyxl
# import xlsxwriter

## Todas las operaciones deben establecer el valor del diccionario '' a True o false
## OperaciónCorrecta = {Falso|Verdadero}
##

def load_source_main (datasources, mainParams, stepdict = None ):
    # _main_ds siempre hará referencia a la fuente de datos original donde se estará trabajando
    
	"""
	Función para cargar los datos base o main que se utilizarán.

	"""
    
	register_count = dhRep.register_count('DataLoads')
	if register_count > 1:
		datasources['_main_ds'] = dhRep.join_chunk_data('DataLoads')
		datasources['chunks'] = register_count
		return True, datasources['_main_ds']
	else:
		dictObj = dhRep.obtener_atributos_por_docid_prj('DataLoads', mainParams['source_id'], ['schema','data'] )
		datasources['_main_ds'] = pd.read_json(StringIO(json.dumps(dictObj)), orient='table')
		datasources['chunks'] = 1
		return True, datasources['_main_ds']

def save_source_main (datasources, mainParams, stepdict = None ):
    
    """
    Función para guardar los datos base o main que se utilizarán.
    
    """
    
    if datasources['chunks'] > 1:
        df_chunks = dhUtilities.chunk_partitioning_save(datasources['_main_ds'], datasources['chunks'])
        dhRep.delete_chunk_data(stepdict['collection'])
        for chunk in df_chunks:
            doc = json.loads(chunk.to_json(orient='table'))
            dhRep.InsertarDocumentoBDProyecto (stepdict['collection'], doc)
        return True, datasources['_main_ds']

    else:
        doc =  json.loads(datasources['_main_ds'].to_json(orient='table'))
        doc['_id'] = ObjectId(mainParams['source_id'])
        dhRep.EliminarDocumentoProyecto (stepdict['collection'], doc)
        dhRep.InsertarDocumentoBDProyecto (stepdict['collection'], doc)
        return True, datasources['_main_ds']

def apply_synonymous(datasources, mainParams, stepdict = None):
    #operacion para aplicar sustitución por sinónimos a una columna origen y coloca el resultado en la columna destino
    dtFrDatos = datasources['_main_ds']
    filtro={ 'rule_type':'SINONIMO','rule_name': stepdict['rule_name'] }
    columna_fuente = stepdict['column_src']
    columna_destino = stepdict['column_dest']

    if stepdict['column_dest'] != stepdict['column_src'] :
        dtFrDatos[columna_destino] = dtFrDatos[columna_fuente]

    ReglasDict = dhRep.obtener_atributos_por_filtro_prj('Rules', filtro , ['search_value','change_value'] )
    for regla in ReglasDict:
        dtFrDatos[columna_destino] = dtFrDatos[columna_destino].str.replace(regla['search_value'], regla['change_value'])

    log.registrar_ejecucion_exitosa_operacion_dataflow_prj (mainParams['flow_id'], stepdict )
    return True, None

def validate_sourcecolumns_vs_layout (datasources, mainParams, stepdict = None):
    mapeoColumnas = dict()
    dtFrDatos = datasources['_main_ds']
    layout = dhRep.BuscarDocumentoBDProyecto('Layouts', 'name' , stepdict['layout_name'])

    for col in layout['columns']:
        if layout['header']==True:
            for al in col['alias_source']:
                if al in dtFrDatos.columns:
                    mapeoColumnas[ col['column_name'] ] = al
                    col['column_name_source'] = al
            if col['column_name'] not in mapeoColumnas:
                mapeoColumnas[col['column_name']] = ''
        else:
            col['column_name_source'] = dtFrDatos.columns[ col['column_position_source'] ] \
                if col['column_position_source'] >=0 and col['column_position_source'] < len(dtFrDatos.columns) else ''

    mapeoOk = False if '' in mapeoColumnas.values() else True

    if mapeoOk:
        stepdict['execute_status'] = 'Ejecution.OK'
        datasources['_main_layout'] = layout
    else:
        nombres_columnas_error = ''
        for col in mapeoColumnas:
            for column_name in mapeoColumnas:
                nombres_columnas_error += column_name + ', ' if mapeoColumnas[column_name] == '' else ''
        stepdict['execute_status'] = 'Ejecution.ERROR'
        stepdict['execute_error_text'] = 'La fuente no cumple con las columnas especificadas en el Layout ' + layout['name'] + ': '+ nombres_columnas_error

    return mapeoOk, layout

def extract_layout_from_source (datasources, mainParams, stepdict = None):
    layout = datasources['_main_layout']
    if datasources['_main_layout'] is None:
        validacion, layout = validate_sourcecolumns_vs_layout (datasources, mainParams, stepdict)
        if validacion == False:
            return False, None

    dtFrDatos = datasources['_main_ds']
    nombresColumnas =  [ column['column_name_source'] for column in layout['columns'] ]
    dtFrDatos = pd.DataFrame( dtFrDatos[ nombresColumnas] )
    dtFrDatos.rename (columns={ column['column_name_source'] : column['column_name'] for column in layout['columns'] }, inplace=True)
    datasources['_main_ds'] = dtFrDatos

    return True, dtFrDatos

def validate_vs_layout_datatypes (datasources, mainParams, stepdict = None):
    layout = datasources['_main_layout']
    dtFrDatos = datasources['_main_ds']
    for col in layout['columns']:
        resul = dtFrDatos[col['column_name']].apply(
            lambda cl: dhUtilities.ValidarFormatoObjeto(cl, col['data_type'], col['allow_null']))

        if len(resul) > 0:
            resul = resul[resul == False]
            if len(resul) > 0:
                conj = set(dtFrDatos.loc[resul.index, col['column_name']].fillna('(vacio)'))
                stepdict['execute_status'] = 'Ejecution.ERROR'
                stepdict['execute_error_text'] = '' if 'execute_error_text' not in stepdict else stepdict['execute_error_text']
                stepdict['execute_error_text'] = '\nValores en la Columna {} no cumplen con el Formato {} >>> {}'.format(col['column_name'], col['data_type'], conj)

                print(
                    '\nValores en la Columna {} no cumplen con el Formato {} >>> {}'.format(col['column_name'],
                                                                                               col['data_type'], conj))
    return True, None

def validate_numeric_range (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    nombre_columna = stepdict['column_src']


    dtfNoValidos=dtFrDatos[nombre_columna].copy()
    dtfNoValidos[:] = False

    filtro={ 'rule_type':'RANGO NUMERICO','rule_name': stepdict['rule_name'] }
    ReglasDict = dhRep.obtener_atributos_por_filtro_prj('Rules', filtro, ['min_value', 'max_value'])

    for regla in ReglasDict:
        Minimo = regla['min_value']
        Maximo = regla['max_value']
        dtfNoValidos = (dtFrDatos[nombre_columna] < Minimo) | dtfNoValidos
        dtfNoValidos = (dtFrDatos[nombre_columna] > Maximo) | dtfNoValidos

    dtfNoValidos = dtFrDatos[dtfNoValidos[:]==True][nombre_columna].unique()

    if len (dtfNoValidos ) > 0:
        stepdict['execute_status'] = 'Ejecution.ERROR'
        stepdict['execute_error_text'] = '\nValores en la Columna {} no cumplen con el rango ({}-{}) >>> {}'.format(nombre_columna, Minimo, Maximo, dtfNoValidos)
        return False, None

    return True, None

def validate_exist_in_catalog (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    dictObj = dhRep.obtener_atributos_por_docid_prj('MasterDataCatalog', stepdict['catalog_id'], ['schema','data'] )
    valores_catalogo = pd.read_json(json.dumps(dictObj), orient='table')
    valores_unicos = dtFrDatos[stepdict['column_src']].unique()
    valores_catalogo = valores_catalogo[stepdict['key_column_name']].to_list()
    Valores_no_existentes = list()

    for valor in valores_unicos:
        if valor not in valores_catalogo:
            Valores_no_existentes.append(valor)

    if len(Valores_no_existentes) > 0:
        stepdict['execute_status'] = 'Ejecution.ERROR'
        stepdict['execute_error_text'] = '\nValores en la Columna {} no existen en el catálogo {}: {}'.format(stepdict['column_src'], stepdict['catalog_name'],  Valores_no_existentes)
        return False, None

    return True, None

def apply_join_from_value_vs_catalog (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    dictObj = dhRep.obtener_atributos_por_docid_prj('MasterDataCatalog', stepdict['catalog_id'], ['schema','data'] )
    valores_catalogo = pd.read_json(json.dumps(dictObj), orient='table')
    dtt = valores_catalogo.set_index(stepdict['key_column_name'])
    dataJoin = dtFrDatos.join(dtt, on=stepdict['column_src'], rsuffix='_B' )
    dtFrDatos[stepdict['column_dest']] = dataJoin[stepdict['value_column_name']]
    return  True, None

def apply_mask (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    fmt = stepdict['mask_string']
    dtFrDatos[ stepdict['column_dest'] ]  = [ fmt.format( valor ) for valor in  dtFrDatos[ stepdict['column_src'] ] ]
    return True, None

def extract_mask_from_text (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    mascara = stepdict['mask_string']
    dtFrDatos[stepdict['column_dest']] = dtFrDatos[stepdict['column_src']].str.extract(r''+mascara, expand=False)
    return True, None

def extract_words_by_position (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    re_Delimitador = '\\' + stepdict['separator']
    ini = stepdict['init_position']
    fin = stepdict['final_position']
    clCount = dtFrDatos[stepdict['column_src']].str.count(re_Delimitador).fillna(0).astype(int) + 1
    nMaxSep = clCount.max().astype(int) - 1

    def fnConcat (arr, ini, fin, sep):
        x = ''
        fin =  (fin if fin < len(arr) else len(arr))+1
        for i in range(ini, fin):
            x+= arr[i] + sep
        return x

    ser_Valores = dtFrDatos[stepdict['column_src']].str.split(re_Delimitador)
    dtFrDatos[stepdict['column_dest']] = ser_Valores.apply(lambda arr: fnConcat(arr,ini,fin, stepdict['separator'])  )

    return True, None

def validar_fonetico(datasources, mainParams, stepdict = None):
    """
    Valida una columna dada por medio del algoritmo fonético soundex, así como su distribución en el dataframe.
    :param dict: Diccionario con los valores de los parámetros utilizados por esta operación.
        :col_origen: Columna origen de donde se extrae el dato.
        Ejemplo:
        step_dict = {
            'col_origen' : "Nombre"
        }

    :return: (ResultadoExitoso, DataFrameResultado)
        ResultadoExitoso: Verdadero si la ejecución de la función ocurrió sin problemas, Falso en caso contrario
        DataFrameResultado: Dataframe con la columna de llaves añadida.

    """
    df_main = datasources['_main_ds']
    origen = stepdict['col_origen']
    result = pd.DataFrame()
    result[origen] = df_main[origen]
    result["soundex"] = result[origen].apply(lambda x: jellyfish.soundex(x))
    result['freq soundex'] = result['soundex'].apply(
      lambda x: result.soundex.str.contains(x).sum()
    )
    result["soundex dist%"] = (result["freq soundex"] / len(df_main.index))*100

    result["metaphone"] = result[origen].apply(lambda x: jellyfish.metaphone(x))
    result['freq metaphone'] = result['metaphone'].apply(
      lambda x: result.metaphone.str.contains(x).sum()
    )
    result["metaphone dist%"] = (result["freq metaphone"] / len(df_main.index))*100
    result = result.drop_duplicates()
    
    doc = json.loads(result.to_json(orient='table'))
    doc['name'] = "Foneticos - " + origen
    dhRep.InsertarDocumentoBDProyecto ("DataPerf", doc)
    return True, result


def windowKey(datasources, mainParams, stepdict = None):
    
    """
    Función encargada de generar una window key para los datos utilizando las
    columnas y métodos especificados por el usuario.
    
    Argumentos:
        data (DataFrame) dataframe que contiene la base de datos.
        cols (lst) lista de columnas a utilizar para generar la window key.
        methods (lst) lista de métodos a utilizar. Para soundex el método es
            'sou' y para substring es 'sub'.
        substring_length (int) número entero que nos indica la longitud que
            tendrá el substring.
        upper (bool) valor booleano que nos indica si el substring será en
            minúscula o mayúscula.
        
    Regresa:
        una lista que contiene las window keys generadas para el dataset en
        cuestión.
        
    """
    
    df_main = datasources['_main_ds']

    func_dict = {i: [stepdict['cols'][i], stepdict['methods'][i]] for i in range(len(stepdict['cols']))}

    windowKey = []

    for i in range(len(func_dict)):
        
        if func_dict[i][1] == "sou":
            soundex = np.vectorize(jellyfish.soundex)
            windowKey.append(soundex(df_main[func_dict[i][0]].values))
        if func_dict[i][1] == "sub":
            if stepdict['upper'] == True:
                substring = np.vectorize(lambda x: x[:stepdict['slength']].replace(' ', '').upper() if (len(x) == stepdict['slength']) else (x[:stepdict['slength']].replace(' ', '').upper() + (' ' * (stepdict['slength'] - len(x)))))
                windowKey.append(substring(df_main[func_dict[i][0]].values))
            else:
                substring = np.vectorize(lambda x: x[:stepdict['slength']].replace(' ', '') if (len(x) == stepdict['slength']) else (x[:stepdict['slength']].replace(' ', '') + (' ' * (stepdict['slength'] - len(x)))))
                windowKey.append(substring(df_main[func_dict[i][0]].values))
    
    df_main["WindowKey"] = np.array(map(''.join, zip(*windowKey)))

    return True, None

def calculate_expression (datasources, mainParams, stepdict = None):
    """
    Opera dos columnas con una expresión determinada por un operador.
    :param dict: Diccionario con los valores de los parámetros utilizados por esta operación.
        :value_1: Primera columna a operar.
        :value_2: Segunda columna a operar.
        :col_dest: Columna destino donde se guardará el resultado.
        :operator: Operador que se usará con las columnas.
        Ejemplo:
        step_dict = {
            'value_1' : "unite_price",
            'value_2' : "quantity",
            'col_dest' : "total price",
            'operator' : "*",
        }

    :return: (ResultadoExitoso, DataFrameResultado)
        ResultadoExitoso: Verdadero si la ejecución de la función ocurrió sin problemas, Falso en caso contrario
        DataFrameResultado: Dataframe con la columna de llaves añadida.

    """
    df_main = datasources['_main_ds']
    value_1 = stepdict['value_1']
    value_2 = stepdict['value_2']
    dest = stepdict['col_dest']
    oper = stepdict['operator']
    
    if df_main[value_1].dtype.name == "object" or df_main[value_2].dtype.name == "object":
        return False, df_main

    ops = {'+' : operator.add, '-' : operator.sub, '*' : operator.mul, '/' : operator.truediv, }
    df_main[dest] = df_main.apply(lambda row : ops[oper](float(row[value_1]), float(row[value_2])), axis=1)
    return True, df_main

def create_mask(datasources, mainParams, stepdict = None):
    src = stepdict['column_src']
    dest = stepdict['column_dest']
    def get_mask(dato):
        mask='' 
        for c in dato:
            if c.isdigit():
                mask += 'N'
            elif not c.isprintable():
                mask += 'H'
            elif c.isalpha():
                mask += 'A'
            else:
                mask += str(c)
        return mask
    result = datasources['_main_ds']
    result[dest] = result[src].apply(
    lambda dato: get_mask(str(dato))
    )
    return (True, result)

def get_value_freq(datasources, mainParams, stepdict = None):
    df_main = datasources['_main_ds']
    col_src = stepdict['column_src']
    col_id = stepdict['column_id']
    separator = stepdict['separator']
    one_word = stepdict['one_word']
    init_pos = stepdict['init_pos']
    final_pos = None if stepdict['final_pos'] == "None" else stepdict['final_pos']
    if final_pos != None and final_pos < init_pos:
        return False, "Posición final mayor que posición inicial."
    new_column = []
    ids = []
    def iterate_words(row):
        words = str(row[col_src]).split(separator)[init_pos:final_pos]
        data_id = row[col_id]
        new_column.extend(words)
        ids.extend(repeat(data_id, len(words)))
        if one_word:
            return True
        else:
            for x in range(2, len(words)+1):
                new_column.append(separator.join(words[0:x]))
                ids.append(data_id)
    df_main.apply(lambda row: iterate_words(row), axis=1)
    df_final = pd.DataFrame({
        'Phrase' : new_column,
        'Id' : ids, 
    })
    df_final['Words'] = df_final['Phrase'].apply(
        lambda x: len(x.split(separator))
    )
    df_final['Frequency'] = df_final['Phrase'].apply(
        lambda x: df_final.Phrase.str.contains(x).sum()
    )
    df_final['Dst %'] = round(((df_final['Frequency'] / df_final.shape[0])*100), 3)
    df_final["Category"] = ""
    doc = json.loads(df_final.to_json(orient='table'))
    doc['name'] = "Frequency - " + col_src
    dhRep.InsertarDocumentoBDProyecto ("DataPerf", doc)
    return True, df_final

# def window_key(datasources, mainParams, stepdict = None):
#     dataframe = datasources['_main_ds']
#     dataframe["window_key"]=""
#     vocales = "AEIOUaeiou"
#     consonantes = "bcdfghjklmnpqrstwxyzñ"
#     consonantes = consonantes + consonantes.upper()

#     #Funnción que obtiene las vocales de un dato.
#     def get_vowels(dato, rango, repetir = True, actual=''):
#         res = actual
#         for c in dato[0:None]:
#             if (len(res) == rango):
#                     return res
#             if c in vocales:
#                 if (not repetir and c not in res):
#                     res += c
#                 if (repetir):
#                     res += c 
#         return res

#     #Funnción que obtiene las consonantes de un dato.
#     def get_consonants(dato, rango, repetir = True, actual=''):
#         res = actual
#         for c in dato[0:None]:
#             if (len(res) == rango):
#                     return res
#             if c in consonantes:
#                 if (not repetir and c not in res):
#                     res += c
#                 if (repetir):
#                     res += c
#         return res 

#     #Función que obtiene cualquier caractér de un dato en un rango especificado.
#     def get_any(dato, rango, repetir = True, actual=''):
#         res = actual
#         for c in dato[0:None]:
#             if (len(res) == rango):
#                 return res
#             if (not repetir and c not in res):
#                 res += c
#             if (repetir):
#                 res += c
#         return res  

#     #Se obtienen los valores de los diccionarios
#     columnas = stepdict.get('columnas')
#     reglas = stepdict.get('reglas')
#     rangos = stepdict.get('rangos')
#     repetidos = stepdict.get('repetir')

#     #Se valida que la longitud de las listas de parámetros sea la misma.
#     is_valid = len(columnas) == len(reglas) and len(reglas) == len(rangos) and len(rangos) == len(repetidos)
#     #En caso de que no, se regresa False y el dataframe sin llaves.
#     if not is_valid:
#         return False, dataframe

#     #Se recorre cada parámetro por regla
#     for x in range(len(columnas)):
#         columna = columnas[x]
#         selection = reglas[x]
#         rango = rangos[x]
#         repetir = repetidos[x]
        
#         #Vocales
#         if ("A" == selection):
#             dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
#                 lambda x: get_any(x, rango, repetir = repetir)
#                 ) 
#         elif ("V" == selection):
#             dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(lambda x: get_vowels(x,rango, repetir = repetir))
#         elif ("FV" == selection):
#             dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
#                 lambda x: get_vowels(x[1:], rango, actual=x[0], repetir=repetir)
#                 ) 
#         elif ("FV2" == selection):
#             dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
#                 lambda x: get_vowels(x[1:], rango, actual=x[0], repetir=repetir)
#                 ) 

#         #Consonantes    
#         elif ("C" == selection):
#             dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(lambda x: get_consonants(x,rango, repetir = repetir))
            
#         elif ("FC" == selection):
#             dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
#                 lambda x: get_consonants(x[1:], rango, actual=x[0], repetir=repetir)
#                 )

#         elif ("FC2" == selection):
#             dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
#                 lambda x: get_consonants(x[1:], rango,  actual=x[0], repetir=repetir)
#                 ) 
#     return True, dataframe

def clean_html(datasources, mainParams, stepdict = None):
    #Se leen los valores de los parámetros.
    df_main = datasources['_main_ds']
    origen = stepdict['col_origen']
    destino = stepdict['col_destino']
    chr_especiales  = stepdict['chr_especiales']
    salto = stepdict['salto_linea']
    titulos_img = stepdict['titulos_img']

    """ Función interna que quita las etiquetas propias del código html y las reemplaza por espacios vacíos."""
    def quitar_etiquetas():
        #Expresión regular para identificar etiquetas.
        exp = re.compile('<.*?>') 
        #Si se buscan títlos de imagenes se buscan las etiquetas img y se obtiene su título.
        if titulos_img:
            df_main[destino] = df_main[destino].apply(
                lambda x: re.sub(exp, '', str(x)) if "<img" not in str(x) else re.search('title="(.*)" st', str(x)).group(1)
                )
        #En caso contrario se quitan todas las etiquetas.
        else:
            df_main[destino] = df_main[destino].apply(
                lambda x: re.sub(exp, '', str(x))
                )
    """ Función interna que quita los carácteres especiales del código html."""
    def quitar_chrs_especiales():
        df_main[destino] = df_main[destino].apply(
            lambda x: html.unescape(str(x))
            )

    #Se crea una copia de la columna origen en la columna destino.
    df_main[destino] = df_main[origen]

    if chr_especiales:
        quitar_chrs_especiales()

    quitar_etiquetas()
    #Si se indica que no se impriman saltos de línea se quitan.
    if not salto:
        df_main[destino]=df_main[destino].str.replace(r'\n', ' ',regex=True)

    return (True, df_main)		

def get_column_type(datasources, mainParams, stepdict = None):
    """
    Función que obtiene información sobre los datos que contiene cada columna, tales como:
        Data Type: Tipo de datos que contiene la columna.
        Max Length: Longitud del valor máximo
        Min Length: Longitud del valor mínimo.
        Max Value: Valor máximo.
        Min Value: Valor mínimo.
        Nulls: True si la columna contiene valores nulos. False en caso contrario. 

    :param dict: Diccionario con los valores de los parámetros utilizados por esta operación.
        Ningún parámetro es necesario para esta operación.

    :return: (ResultadoExitoso, Resulato)
		ResultadoExitoso: Verdadero si la ejecución de la función ocurrió sin problemas, Falso en caso contrario.
		DataFrameResultado: Objeto Json que contiene el resultado del perfilado.
    """

    dataframe = datasources['_main_ds']
    columns = list(dataframe)
    data_info = {}
    max_val = None
    min_val = None

    for col in columns:
        max_len = 0
        min_len = 0
        col_type = dataframe[col].dtype.name

        col_type = "string" if col_type == "object" else col_type
        if col_type == "string":
            #Se obtienen las longitudes máximas y mínimas.
            max_len = int(dataframe[col].str.len().max())
            min_len = int(dataframe[col].str.len().min())

            #Si las longitudes son iguales se comparan por bytes.
            if max_len == min_len:
                max_val = dataframe[col].astype(str).max()
                min_val = dataframe[col].astype(str).min()

            #Si las longitudes son diferentes se obtiene la primera coincidencia de cada una.   
            else:
                max_val = dataframe.iloc[np.where(dataframe[col].str.len() == max_len)[0]]
                max_val = max_val.iloc[0][col]
                min_val = dataframe.iloc[np.where(dataframe[col].str.len() == min_len)[0]]
                min_val = min_val.iloc[0][col]

        #Se castea float64 de numpy por float de python
        elif col_type == "float64":
            max_val = float(dataframe[col].max())
            min_val = float(dataframe[col].min())
            max_len = int(len(str(max_val)))
            min_len = int(len(str(min_val)))

        #Se castea int64 de numpy por int de python
        elif col_type == "int64":
            max_val = int(dataframe[col].max())
            min_val = int(dataframe[col].min())
            max_len = int(len(str(max_val)))
            min_len = int(len(str(min_val)))

        #Se castea Bool de numpy por bool de python
        else:
            max_val = bool(dataframe[col].max())
            min_val = bool(dataframe[col].min())
            max_len = int(len(str(max_val)))
            min_len = int(len(str(min_val)))

        #Se determina si la columna contiene nulos.
        has_nulls = True if (dataframe[col].isna().any()) == True else False

        col_info = {
            "Data Type" : col_type,
            "Max Length" : max_len,
            "Max Value" : max_val,
            "Min Length" : min_len,
            "Min Value" : min_val,
            "Nulls" : has_nulls,
        }

        data_info[col] = col_info

    doc = json.loads(json.dumps(data_info))
    doc['name'] = "Data Summary"
    dhRep.InsertarDocumentoBDProyecto ("DataPerf", doc)
    return True, col_info
    
def get_substring(datasources, mainParams, stepdict = None):
    """
    Función que extrae subcadenas de una columna y las coloca en otra.

    :param dict: Diccionario con los valores de los parámetros utilizados por esta operación.
        :col_origen: Columna origen de donde se extrae la subcadena.
        :col_destino: Columna destino donde se deposita la subcadena.
        :init_word: Posición de la palabra inicial (Empezando por 0).
        :total_words: Total de palabras a extraer.
        :separator: Carácter a utilizar para separar la cadena principal.
        :join_char: Carácter a utilizar para unir las subcadenas extraídas.

        Ejemplo:
        step_dict = {
            'col_origen' : "Product Name",
            'col_destino' : "Short Name",
            'init_word' : 0,
            'total_words' : 2,
            'separator': " ",
            'join_char': " "
        }

    :return: (ResultadoExitoso, DataFrameResultado)
        ResultadoExitoso: Verdadero si la ejecución de la función ocurrió sin problemas, Falso en caso contrario
        DataFrameResultado: Dataframe con la columna de llaves añadida.
    """
    df_main = datasources['_main_ds']
    origen = stepdict['col_origen']
    destino = stepdict['col_destino']
    init_word = int(stepdict['init_word'])
    total_words = int(stepdict['total_words'])
    sep = str(stepdict['separator'])
    join_char = str(stepdict['join_char'])

    df_main[destino] = df_main[origen].apply(
        lambda x: join_char.join(x.split(sep)[init_word:total_words])
    )
    return True, df_main

def concat_columns(datasources, mainParams, stepdict = None):
    """
    Función que concatena valores de diferentes cadenas.

    :param dict: Diccionario con los valores de los parámetros utilizados por esta operación.
        :cols_origen: Arreglo de columnas origen de donde se extrae el dato.
        :col_destino: Columna destino donde se deposita el resultado.
        :join_char: Carácter a utilizar para unir las cadenas.

        Ejemplo:
        step_dict = {
            'col_origen' : ["payment", "unit_price", "quantity"]
            'col_destino' : "Full Price",
            'join_char': " - "
        }

    :return: (ResultadoExitoso, DataFrameResultado)
        ResultadoExitoso: Verdadero si la ejecución de la función ocurrió sin problemas, Falso en caso contrario
        DataFrameResultado: Dataframe con la columna de llaves añadida.
    """
    
    df_main = datasources['_main_ds']
    origen = stepdict["col_origen"].split(', ')
    print(origen)
    dest = stepdict["col_destino"]
    join_char = stepdict["join_char"]
    df_main[dest] = df_main[origen].apply(lambda row: join_char.join(row.values.astype(str)), axis=1)
    return True, df_main



#################################################################
#																#
#					  Clase principal							#	
#   -- Contiene todos las rutinas y subrutinas de limpieza --	#
#																#
#################################################################


#Variable que indica las columnas que contiene el dataframe.
total_cols = None
#Variable que guarda la sabana de datos.
sabana = {}
#Copia del dataframe
df_copy = None
catalogo = {}

def set_cat(ruta):
	global catalogo
	catalogo = {}
	with open(ruta, encoding="utf8") as f:
		for line in f:
			line = line.replace("\n", "")
			tokens = line.split("-")
			key = tokens[0]
			catalogo[key] = tokens[1]
	f.close()
	print(catalogo)

def change_by_cat(df, column):
	'''
	Método que reemplaza valores de abreviaturas de acuerdo a un catálogo precargado.
	'''
	lista = []
	keys = list(catalogo.keys())
	def check(dato):
		if any((match := key) in dato for key in keys):
			lista.append(1)
			dato = dato.replace(match, catalogo[match] + " ")
		else:
			lista.append(0)
		return dato

	df[column] = df[column].apply(lambda x: check(x))
	sabana[column]["Ajuste Abreviatura"] = lista
	return df


def set_sabana(df):
	'''
	Método que inicializa las variables globales.
	:param df: DataFrame a utilizar.
	'''
	global total_cols, sabana, df_copy
	total_cols = list(df)
	df_copy = df.copy()
	sabana = {col: {} for col in total_cols}

def get_sabana():
	''' Método que retorna la sabana de datos.'''
	return sabana


#Método que busca longitudes 1 y 4. Modificar para usabilidad.
def rm_by_len_or(df, column):
    
	"""
	Método que modifica valores de una columna de acuerdo a su longitd.
	"""

	lista=[]
 
	def check_len(dato):
		dato = str(dato)
		if len(dato) == 1:
			dato = ""
			lista.append(1)
		elif len(dato) == 4:
			dato = "0" + dato
			lista.append(1)
		else:
			dato = dato
			lista.append(0)
		return dato

	df[column] = df[column].apply(lambda x: check_len(x))
	sabana[column]["Ajuste longitud"] = lista

	return df


def check_no_ex(df, column):
    #Método interno solicitado por edenred.
	"""
    Método que elimina valores de una columna que son 100% compuestois por alfa numéricos.

	"""
	lista = []
	def check(dato):
		dato = str(dato)
		## Si no es 100% alnum retorna False

		flag = any(c.isalnum() for c in dato)
		
		if len(dato) == 1 and dato.isalnum() or flag==False:
			dato = ""
			lista.append(1)
		else:
			lista.append(0)
		return dato

	df[column] = df[column].apply(lambda x: check(x))
	sabana[column]["Ajuste NoEx"] = lista
	return df


def check_no_in(df, column):
	lista = []
	def check(dato):
		dato = str(dato)
		## Si es 100% alnum retorna False

		flag = any(c.isalnum() for c in dato)
		if flag:
			lista.append(0)
		else:
			lista.append(1)
			dato = "S/N"
		return dato
		

	df[column] = df[column].apply(lambda x: check(x))
	sabana[column]["Ajuste NoIn"] = lista
	return df


def check_two_cols(df, col1, col2):
	#Método solicitado por Edenred. Modificar para usabilidad.
	'''
	Método que elimina valores de una columna de acuerdo a otra.
	'''
	lista = []
	def check(dato_1, dato_2):
		if dato_1 == "" and not dato_2 == "A":
			dato_1 = "Inactivo"
			lista.append(1)
		else:
			lista.append(0)
		return dato_1

	df[col1] = df.apply(lambda x: check(x[col1], x[col2]), axis=1)
	sabana[col1]["Ajuste GUDIRE"] = lista

	return df

def rm_negativos(df, column):
	'''
	Método que elimina números negativos de una columna numerica.
	'''
	lista = []
	def check(dato):
		dato = str(dato)
		if dato != "" and dato[0] == "-":
			lista.append(1)
			dato = ""
		else:
			lista.append(0)
		return dato

	df[column] = df[column].apply(lambda x: check(x))
	sabana[column]["Remover Negativos"] = lista
	return df

def rm_by_comp(df, column):
	lista = []
	def check(dato):
		dato = str(dato)
		flag = flag = any(c.isalnum() for c in dato)
		if flag == False:
			lista.append(1)
			dato = ""
		else:
			lista.append(0)
		return dato

	df[column] = df[column].apply(lambda x: check(x))
	sabana[column]["Ajuste AFNORE"] = lista
	return df

def trim_col(df, columns, all = False):
	'''
	Método que elimina espacios al principio, final e intermedios extras para una columna dada.
	:param df: DataFrame a utilizar.
	:param columns: Lista de columnas donde se aplica la rutina.
	:param all: True se se eliminan todos los espacios que se encuentren. False en caso contrario.
	'''
	lista = []
	def rm_blanks(dato):
		# Método interno de evaluación por dato
		dato = str(dato)
		if not all:
			if dato.count(" ") >= len(dato.split()):
				lista.append(1)
				dato = dato.strip()
				dato = re.sub(' +', " ", dato)
			else:
				lista.append(0)
		else :
			if dato.count(" ") >= 1:
				lista.append(1)
				dato = re.sub(re.compile(r'\s+'), '', dato)
			else:
				lista.append(0)
		return dato 

	# Se aplica lambdas por columna dada para limpiar los datos
	for col in columns:
		df[col] = df[col].apply(
			lambda x: rm_blanks(x)
		)
		# Por cada columna se actualiza la sabana de datos.
		"""if not all:
			sabana[col]["Espacios extras"] = lista
		else: 
			sabana[col]["Todos los espacios"] = lista
		lista = []"""

	return df
	
def rm_nan(df, columns):
	'''
	Método que remueve los valores NAN insertados por python.
	'''
	def remove(dato):
		dato = str(dato)
		if dato == "NAN" or dato == "nan":	
			dato = ""
		return dato

	for col in columns:
		df[col] = df[col].apply(
			lambda x: remove(x)
		)
	return df

def rm_especial_chars(df, columns, exclude = None ):
	"""
	Método que elimina caracteres especiales, a excepción del espacio, de una serie de columnas dada.
	:param df: DataFrame a utilizar.
	:param columns: Lista de columnas donde se aplica la rutina.
	:params exclude: Lista de valores a omtir, los cuales no serán removidos.
	"""
	lista = []
	def rm_chars(dato):
	# Método interno de evaluación y reemplazo por dato.
		dato = str(dato)
		#Bandera que indica si tiene carácteres especiales.
		flag = False
		if "CARR" in dato:
			lista.append(0)
			return dato
			
		for c in dato:
			if  exclude is None:
				if not c == " " and not c.isalpha() and not c.isdigit():
				
					#Si encuentra uno se cambia la bandera
					flag = True
					dato = dato.replace(c, "")
			else :
				if not c in exclude and not c == " " and not c.isalpha() and not c.isdigit():
				
					#Si encuentra uno se cambia la bandera
					flag = True
					dato = dato.replace(c, "")
		if flag:
			lista.append(1)
		else:
			lista.append(0)	
		return dato
	
	# Aplicación de reglas por cada columna dada.
	for col in columns:
		df[col] = df[col].apply(lambda x: rm_chars(x))
		sabana[col]["Special Chars"] = lista
		lista = []
  
	return df

def upper_col(df, columns):
	"""
	Método que elimina pone en mayusculas los dato de una serie de columnas.
	:param df: DataFrame a utilizar.
	:param columns: Lista de columnas donde se aplica la rutina.
	"""
	lista = []
	def upper_data(dato):
	# Método interno de evaluación y reemplazo por dato
		dato = str(dato)
		if not dato.isupper() and not dato.isnumeric() and dato != "" and dato!="NAN" and dato!="nan":
			lista.append(1)
			dato = dato.upper()
		else:
			lista.append(0)
		return dato
	for col in columns:
		df[col] = df[col].apply(lambda x: upper_data(x))
		sabana[col]["Upper"] = lista
		lista = []
	return df

def rm_accents(df, columns):
	"""
	Método que elimina y reemplaza los acentos en una serie de columnas.
	Args:
		df (DataFrame): DataFrame a utilizar.
		columns (List): Lista de columnas en donde se aplica la regla.
	Returns:
		Retorna el DataFrame modificado.
	"""
	lista = []
	def accents(dato):
		dato = str(dato)
		rm_dato = unidecode.unidecode(dato)
				
		if dato == rm_dato or dato == "" or dato=="NAN" or  dato=="nan":
			lista.append(0)
		else:
			lista.append(1)
			
		return rm_dato

	for col in columns:
		df[col] = df[col].apply(lambda x: accents(x))
		sabana[col]["Accents"] = lista
		lista = []
	return df

def rm_by_len(df, columns, length):
	'''
	Método que remueve valores de acuerdo a una longitud máxima.
	:param columns: Lista de columnas en donde aplicar la rutina.
	:param length: Longitud máxima para validar los datos.
	'''
	lista = []
	def check_len(dato):
		dato = str(dato)
		if len(dato)<length:
			dato = ""
			lista.append(1)
		else :
			lista.append(0)
		return dato
		
	for col in columns:
		df[col] = df[col].apply(lambda x: check_len(x))
		sabana[col]["Check Len"] = lista
		lista = []
	return df

def rm_one_char(df, columns):
	"""
	Método que elimina valores de longitud 1.
	:param df: DataFrame a utilizar.
	:param columns: Lista de columnas donde se aplica la rutina.
	"""
	lista = []
	def remove_char(dato):
		dato = str(dato)
		#Se evalua la longitud.
		if len(dato) == 1:
			lista.append(1)
			dato = ""
		else:
			lista.append(0)
		return dato
	
	for col in columns:
		df[col] = df[col].apply(lambda x: remove_char(x))
		sabana[col]["1 char"] = lista
		lista = []
	return df

def is_float(dato):
	try:
		float(dato)
		return True
	except:
		return False

def replace_char(df, columns, values, sencond_val):
	'''
	Método que busca y reemplaza valores por otro seleccionado.
	:param columns: Lista de columnas donde se aplica la rutina.
	:param values: Lista de valores a reemplazar.
	:param second_val: Valor por el que serán reemplazados los valores anteriores.
	'''
	lista = []
	def rep(dato):
		dato = str(dato)
		flag = False
		for value in values:
			if value in dato:
				flag = True
				dato = dato.replace(value, sencond_val)
		if flag:
			lista.append(1)
		else:
			lista.append(0)
		return dato

	for col in columns:
		df[col] = df[col].apply(lambda x: rep(x))
		sabana[col]["Replace char"] = lista
		lista = []
	return df

def rm_floats(df, columns):
	'''
	Método que remueve valores flotantes de una lista de columnas.
	'''
	lista = []
	def check_floats(dato):
		dato = str(dato)
		if (not dato.isnumeric() and is_float(dato)) or "." in dato:
			dato = ""
			lista.append(1)
		else:
			lista.append(0)
		return dato
	
	for col in columns:
		df[col] = df[col].apply(lambda x: check_floats(x))
		sabana[col]["Is Float"] = lista
		lista = []
	return df

def rm_parentheses(df, columns):
	'''
	Método que remueve cadenas que se encuentren entre paréntesis en las columnas señaladas.
	'''
	lista = []
	def rm_par(dato):
		dato = str(dato)
		if "(" in dato and ")" in dato:
			lista.append(1)
			dato = re.sub(r'\([^)]*\)', '', dato)
		else :
			lista.append(0)
		return dato
	for col in columns:
		df[col] = df[col].apply(lambda x: rm_par(x))
		sabana[col]["parentheses"] = lista
		lista = []
	return df

def rm_alpha(df, columns):
	"""
	Método que elimina caracteres alfabéticos de un dato.
	:param df: DataFrame a utilizar.
	:param columns: Lista de columnas donde se aplica la rutina.
	"""
	lista = []
	def rm_chars(dato):
	# Método interno que realiza la evaluación por dato.
		dato = str(dato)
		# Bandera que indica si se aplica la regla o no.
		flag = False
		numbers = dato.split(",")

		if dato == "" or dato=="NAN" or dato=="nan":
			lista.append(0)
			return dato

		if len(numbers)>1:
			flag = True
			dato = numbers[0]
		
		dato = clean_first(dato)
		numbers = dato.split()
		dato = numbers[0] if len(numbers)>0 else dato
			
		if flag:
			lista.append(1)
		else:
			lista.append(0)
		return dato

	for col in columns:
		df[col] = df[col].apply(lambda x: rm_chars(x))
		sabana[col]["Remove Alpha"] = lista
		lista = []
	return df

def rep_nulls(df, columns, val):
	"""
	Método que reemplaza valores nulos encontrados en una columna.
	Args:
		df (DataFrame): DataFrame a utilizar.
		columns (list): Lista de columnas en donde se aplica la regla.
		val (string): Valor por el que se reemplazan los nulos.
	"""
	lista = []
	def replace_nulls(dato, val):
		if dato == "":
			lista.append(1)
			dato = val
		else:
			lista.append(0)
		return dato

	for col in columns:
		df[col] = df[col].apply(lambda x: replace_nulls(x, val)) 
		sabana[col]["Replace Nulls"] = lista
		lista = []
	return df

def check_email(df, columns):
	"""
	Método que elimina correos encontrados que no sigan cierta estructura.
	Args:
		df (DataFrame): DataFrame a editar.
		columns (List):	Lista a columnas en donde se aplica la regla. 
	Returns:
		Retorna el DataFrame modificado
	"""
	
	lista = []
	def check(dato):
		dato = str(dato)
		dato = dato.split('/')[0] if "/" in dato else dato.split(';')[0]
		if "/" in dato:
			dato = dato.split('/')[0]
		elif ";" in dato:
			dato = dato.split(';')[0]
		elif "," in dato:
			dato = dato.split(',')[0]
		else:
			dato = dato.split(" ")[0]

		regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
		if not (re.fullmatch(regex, dato) ):
			lista.append(1)
			dato = ""
		else:
			lista.append(0)
		return dato

	for col in columns:
		df[col] = df[col].apply(lambda x: check(x)) 
		sabana[col]["Estructura Email"] = lista
		lista = []

	return df
	
def set_year(df, columns):
	"""
	Método que valida y reemplaza los valores de año fuera de rango.
	Args:
		df (DataFrame): DataFrame a utilizar.
		columns (Lista): Lista de columnas en donde se aplica la regla.
	Returns:
		Retorna el DataFrame modificado. 
	"""
	lista = []
	def adjust(dato):
		year = date.today().year
		if int(year) < int(dato):
			lista.append(1)
			dato = year
		elif int(dato) < 1900:
			dato = 1900
			lista.append(1)
		else:
			lista.append(0)
		return dato
	for col in columns:
		df[col] = df[col].apply(lambda x: adjust(x)) 
		sabana[col]["Ajuste año"] = lista
		lista = []
	return df

def set_month(df, columns):
	"""
	Método que valida y reemplaza los valores de mes fuera de rango.
	Args:
		df (DataFrame): DataFrame a utilizar.
		columns (Lista): Lista de columnas en donde se aplica la regla.
	Returns:
		Retorna el DataFrame modificado. 
	"""
	lista = []
	def adjust(dato):
		if int(dato) > 12:
			lista.append(1)
			dato = 12
		elif int(dato) < 1:
			lista.append(1)
			dato = 1
		else:
			lista.append(0)
		#Dar formato de dos digitos.
		dato = ("{:02d}".format(int(dato)))
		return dato

	for col in columns:
		df[col] = df[col].apply(lambda x: adjust(x)) 
		sabana[col]["Ajuste mes"] = lista
		lista = []
	return df
		
def set_day(df, columns):
	"""
	Método que valida y reemplaza los valores de día fuera de rango.
	Args:
		df (DataFrame): DataFrame a utilizar.
		columns (Lista): Lista de columnas en donde se aplica la regla.
	Returns:
		Retorna el DataFrame modificado. 
	"""
	lista = []
	def adjust(dato):
		if int(dato) > 31:
			lista.append(1)
			dato = 31
		elif int(dato) < 1:
			lista.append(1)
			dato = 1
		else:
			lista.append(0)
		# Dar formato de dos digitos.
		dato = ("{:02d}".format(int(dato)))
		return dato
	
	for col in columns:
		df[col] = df[col].apply(lambda x: adjust(x))
		sabana[col]["Ajuste dia"] = lista
		lista = []
	return df

def concat_year(df):
	# Método que concatena los valores de fecha en una sola columna.
	df["CreationDate"] = df["Clanal"].astype(str) + df["Clmeal"].astype(str) + df["Cldial"].astype(str)
	return df

def num_to_bool(df, columns):
	"""
	Método reemplaza valores numericos (0, 1) por valores booleanos.
	Args:
		df (DataFrame): DataFrame a utilizar.
		columns (Lista): Lista de columnas en donde se aplica la regla.
	Returns:
		Retorna el DataFrame modificado. 
	"""
	lista = []
	def transform(dato):
		if int(dato) == 1:
			lista.append(1)
			dato = True
		elif int(dato) == 0:
			lista.append(1)
			dato = False
		else: 
			lista.append(0)
		return dato

	for col in columns:
		df[col] = df[col].apply(lambda x: transform(x))
		sabana[col]["Num to bool"] = lista
		lista = []
	return df

def val_cat(df, columns, catalogo):
	"""
	Método que valida y reemplaza los valores que se encuentren fuera de un catálogo dado.
	Args:
		df (DataFrame): DataFrame a utilizar.
		columns (Lista): Lista de columnas en donde se aplica la regla.
		catalogo (Lista): Catálogo que contiene los valores para validar la columna.
	Returns:
		Retorna el DataFrame modificado. 
	"""
	lista = []
	def validar(dato):
		if not dato in catalogo:
			lista.append(1)
			dato = ""
		else:
			lista.append(0)
		return dato

	for col in columns:
		df[col] = df[col].apply(lambda x: validar(x))
		sabana[col]["Val Catalogo"] = lista
		lista = []
	return df

def rm_emails(df, columns):
	'''
	Método que busca y elimina correos electrónicos de una lista de columnas.
	'''
	lista = []
	def rm_mail(dato):
		if "@" in dato or ".com" in dato:
			lista.append(1)
			dato = ""
		else : 
			lista.append(0)
		return dato

	for col in columns:
		df[col] = df[col].apply(lambda x: rm_mail(x))
		sabana[col]["Télefono no válido"] = lista
		lista = []
	return df

def split_ext(df, col_tel, col_ext):
	#Método interno solicitado.
	lista = []
	def get_ext(row):
		dato = str(row[col_tel])
		dato = dato.upper()
		ext = ""
		if "EXT" in dato:
			lista.append(1)
			tels = dato.split("EXT")
			if len(tels) > 1:
				ext = tels[1]
				tel = tels[0]
				row[col_ext] = ext
				row[col_tel] = tel
			else :
				ext = tels[0]
				row[col_ext] = ext
				row[col_tel] = ""
		elif "XT" in dato:
			lista.append(1)
			tels = dato.split("XT")
			if len(tels) > 1:
				ext = tels[1]
				tel = tels[0]
				row[col_ext] = ext
				row[col_tel] = tel
			else :
				ext = tels[0]
				row[col_ext] = ext
				row[col_tel] = ""
		else:
			lista.append(0)

		return row

	df = df.apply(lambda row: get_ext(row), axis = 1)
	sabana[col_tel]["Extensión extraída"] = lista
	sabana[col_ext]["Extensión en tel."] = lista
	lista = []
	return df		

def save_sabana(df, nombre, keys = []):
	"""
	Método que procesa y guarda la sabana creada a partir de las rutinas realizadas.
	Args:
		df (DataFrame): DataFrame a procesar.
		nombre (str): Cadena que indica nombre del archivo a guardar (xlsx).
	"""
	global df_copy
	pivot_keys = df[keys].copy()

	for key in keys:
		df.drop(key, axis=1, inplace=True)
		df_copy = df_copy.drop(key, axis=1)
		total_cols.remove(key)

	writer = pd.ExcelWriter(nombre, engine="xlsxwriter")
	df_rules = pd.DataFrame()
	result = pd.DataFrame()


	cont = 0
	pos = 0
	for key in sabana.keys():
		if key not in keys:
			df_rules.insert(pos, total_cols[cont] + " - Original", df_copy[total_cols[cont]])
			df_rules.insert(pos+1, total_cols[cont] + " - Clean", df[total_cols[cont]])
			values = sabana[key].keys()
			for val in values:
				df_rules.insert(pos+2, val, sabana[key][val])
				df_rules[val] = sabana[key][val]


			pos += 3
			cont += 1

	result = pd.concat([pivot_keys, df_rules], axis=1, join="inner")
	result.to_excel(writer, index = False, sheet_name = "sabana")

	writer.save()

def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))

def count_nums(dato):
	numbers = sum(c.isdigit() for c in dato)
	return numbers

def format_masks(df, col):
	lista =[]
	def format(dato):
		dato = str(dato)
		if not has_numbers(dato):
			dato = ""
			return dato
		
		dato = dato.upper()
		dato = dato.replace("\\", "-")
		dato = dato.replace("/", "-")
		dato = dato.replace("HRS.", "")
		dato = dato.replace("HRS", "")
		dato = dato.replace("HR.", "")
		dato = dato.replace("HR", "")
		dato = dato.replace("DE", "")
		#dato = dato.replace("Y", "A")
		dato = dato.replace("P.M.", "")
		dato = dato.replace("A.M", "")
		dato = dato.replace("PM", "")
		dato = dato.replace("AM", "")
		dato = dato.replace("P:M:", "")
		dato = dato.replace("A:M:", "")

		dato = dato.replace("-", ":") if dato.count("-") == 1 and len(dato) == 3 else dato 
		dato = dato.replace("-", "A") if dato.count("-") == 1 and len(dato) >= 10 else dato 
		dato = dato.replace(".", ":")
		dato = dato.replace(";", ":")

	
		return dato

	df[col] = df[col].apply(lambda x: format(x))
	return df

def rm_except(df, col, exclude):
	'''
	Método que elimina los carácteres de un dato en una columna, exceptuando los señalados.
	'''
	def remove(dato):
		dato = str(dato)
		if not dato == "" and str(dato[0]).isalpha():
			dato = dato.replace(dato[0], "")
		for c in dato:
			if c.isalpha() and not c in exclude:
				dato = dato.replace(c, "")
		return dato

	df[col] = df[col].apply(lambda x: remove(x))
	return df

def get_mask(dato):
	dato = str(dato)
	mask='' 
	for c in dato:
		if c.isdigit():
			mask += 'N'
		elif not c.isprintable():
			mask += 'H'
		elif c.isalpha():
			mask += 'A'
		else:
			mask += c
	return mask

def masks(df, col):
	df["Mask"] = df[col].apply(lambda x: get_mask(x))
	return df

def clean_fst_word(df, col):
	lista = []
	def rm_second(dato):
		dato = str(dato)
		if dato == "FALTA R.F.C.":
			lista.append(0)
			return dato
		words = dato.split()
		if len(words) > 1:
			dato = words[0]
			lista.append(1)
		else:
			lista.append(0)
		return dato

	df[col] = df[col].apply(lambda x: rm_second(x))
	sabana[col]["Remover segundo"] = lista
	lista = []
	return df
	
def clean_first(dato):
	if not dato == "" and (not str(dato[0]).isnumeric()):
		dato = dato[1:]
		return clean_first(dato)
	elif not dato == "" and (not str(dato[-1]).isnumeric()):
		dato = dato[:-1]
		return clean_first(dato)
	else:
		return dato

def format_hours(df, col):
	"""
	Función que, en base a la máscara, cambia la estructura de horas y da formato.
	"Abandonad toda esperanza, quienes aquí entráis"
	Args:
		df (DataFrame): DataFrame a utilizar.
		col (str): Nombre de columna que contiene las horas
	"""
	lista = []
	masks = []
	masks_origen = []
	def format(dato):
		dato = str(dato)
		dato = clean_first(dato)
		dato = re.sub(' +', " ", dato)
		mask = get_mask(dato)
		masks_origen.append(mask)
		########################
		if mask == "N-NN A NN-NN":
			if "A" in dato:
				dato = "0"+dato 
				dato = dato.replace("-", ":")
			elif "Y" in dato:
				rangos = dato.split(" Y ")
				dato = "0" + dato[0] + ":00 A " + rangos[1].split("-")[1] + ":00"
				
		elif mask == "N:NN A NN:NN":
			dato = "0"+dato
		elif mask == "NN-NN A NN-NN":
			dato = dato.replace("-", ":")
		elif mask == "N:NN A N:NN":
			rangos = dato.split(" A ")
			rangos[0] = "0" + rangos[0]
			rangos[1] = "0" + rangos[1]
			dato = " A ".join(rangos)
		elif mask == "N A NN":
			dato = "0" + dato
			rangos = dato.split(" A ")
			rangos[0] += ":00"
			rangos[1] += ":00"
			dato = " A ".join(rangos)
		elif mask == "N A NN:NN":
			dato = "0" + dato
			rangos = dato.split(" A ")
			rangos[0] += ":00"
			dato = " A ".join(rangos)
		elif mask == "N-NN A NN-NN:NN":
			rangos = dato.split(" A ")
			dato ="0" + rangos[0][0] + ":00 A "
			dato += rangos[1].split("-")[1]
		elif mask == "N:NN A NN":
			dato = "0" + dato
			dato += ":00"
		elif mask == "N A N A N A N":	
			dato = dato[0] + " A " + dato[-1] #Ej. 2 a 6
			rangos = dato.split(" A ")
			dato = "0" + rangos[0] + ":00 A " + "0" + rangos[1] + ":00"
		elif mask == "N:NN : NN:NN":
			rangos = dato.split(" : ")
			dato = " A ".join(rangos)
			dato = "0" + dato
		elif mask == "N:NN NN:NN":
				dato = "0" + dato
				dato = " A ".join(dato.split())
		elif mask == "NN A NN":
			rangos = dato.split(" A ")
			dato = rangos[0] + ":00 A " + rangos[1] + ":00"
		elif mask == "N A N":
			rangos = dato.split(" A ")
			dato = "0" + rangos[0] + ":00 A 0" + rangos[1] + ":00"
		elif mask == "N-NN NN-NN":
			rangos = dato.split(" ")
			dato = "0" + rangos[0][0] + ":00 A " + rangos[1].split("-")[1] + ":00"
		elif mask == "N-N A N-N":
			dato = "0" + dato[0] + ":00 A 0" + dato[-1] + ":00"
		elif mask == "NN:NN A N:NN":
			rangos = dato.split(" A ")
			dato = rangos[0] + " A 0" + rangos[1]
		elif mask == "N A NN :":
			dato = dato.replace(" :", "")
			rangos = dato.split(" A ")
			dato = "0" + rangos[0] + ":00 A " + rangos[1] + ":00"
		elif mask == "N-NN A NN:NN-NN":
			rangos = dato.split(" A ")
			dato = "0" + dato[0] + ":00 A " + rangos[1].split("-")[1] + ":00"
		elif mask == "NN:NN NN:NN":
			dato = dato.replace(" ", " A ")
		elif mask == "NN NN-NN":
			rangos = dato.split(" ")[1].split("-")
			dato = rangos[0] + ":00 A " + rangos[1] + ":00"
		elif mask == "NN-NN":
			rangos = dato.split("-")
			dato = rangos[0] + ":00 A " + rangos[1]	+ ":00"
		elif mask == "NAN N A N" or  mask == "N A NNAN A N"  or  mask == "N-N N-N" or mask == "N A NAN A N" or mask == "N-NN A N-N":
			dato = "0" + dato[0] + ":00 A 0" + dato[-1] + ":00" 
		elif mask == "N ANN":
			dato = "0" + dato[0] + ":00 A " + dato.split("A")[1] + ":00"
		elif mask == "N NN A N NN":
			rangos = dato.split(" A ")
			dato = "0" + str(rangos[0]).replace(" ", ":") + " A 0" + str(rangos[1]).replace(" ", ":")
		elif mask == "NNNNN NNANN" or mask == "NNNN NNANN":
			rangos = dato.split(" ")[1].split("A")
			dato = rangos[0] + ":00 A " + rangos[1] + ":00"
		elif mask == "NNNN A NN:NN":
			dato = dato[:2] + ":" + dato[2:]
		elif mask == "NNNN-NNNN":
			dato = dato[:2] + ":" + dato[2:7] + ":" + dato[7:]
			dato = dato.replace("-", " A ")
		elif mask == "NNNN - NNNN":
			dato = dato[:2] + ":" + dato[2:9] + ":" + dato[9:]
			dato = dato.replace("-", "A")
		elif mask == "NNNN A NNNN":
			dato = dato[:2] + ":" + dato[2:9] + ":" + dato[9:]
		elif mask == "NNN A NNNN":
			dato =  "0" + dato
			dato = dato[:2] + ":" + dato[2:9] + ":" + dato[9:]
		elif mask == "NNN A NN:NN":
			dato =  "0" + dato
			dato = dato[:2] + ":" + dato[2:]
		elif mask == "NNN A NN":
			dato = "0" + dato +":00"
			dato = dato[:2] + ":" + dato[2:]
		elif mask == "NNN A NNN":
			dato = "0" + dato[:6] + "0" + dato[6:]
			dato = dato[:2] + ":" + dato[2:9] + ":" + dato[9:]
		elif mask == "NNN NNANN"	:
			rangos = dato.split()[1].split("A")
			dato = rangos[0] + ":00 A " + rangos[1] + ":00"
		elif mask == "NNN-NN NN-NN":
			rangos = dato.split()[1].split("-")
			dato = rangos[0] + ":00 A " + rangos[1] + ":00"
		elif mask == "NNNA NN:NN":
			dato = "0" + dato[0] + ":00 A " + dato.split()[1]
		elif mask == "NNNAN:NNNAN:NN":
			dato = "0" + dato[0] + ":00 A 0" + dato.split("A")[-1] 
		elif mask == "NNN: A NN:NN":
			dato = "0" + dato[:1] + ":" + dato[1:2] + " A " + dato.split(" A " )[1]
		elif mask == "NNN NNNN":
			dato = "0" + dato[0] + ":" + dato[1:3] + " A " + dato[4:6] + ":" + dato[6:]
		elif mask == "NN-NN NN-NN":
			rangos = dato.split()[1].split("-")
			dato = rangos[0] + ":00 A " + rangos[1] + ":00"
		elif mask == "NN:NNA NN:NN":
			dato = dato.replace("A", " A")
		elif mask == "NN ANN:NN":
			dato = dato.replace("A", "A ")
			dato = dato[:2] + ":00" + dato[2:]
		elif mask == "NN:NN A NN":
			dato = dato + ":00"
		elif mask == "NN:NNANNNN":
			dato = dato[:8] + ":" + dato[8:]
			dato = dato.replace("A", " A ")
		elif mask == "NN:NN A NNANN":
			dato = dato[:10] + ":" + dato[11:]
		elif mask == "NNA NN":
			dato = dato.replace("A", ":00 A")
			dato = dato + ":00"
		elif mask == "NN NNANN":
			dato = dato.split()[1]
			dato = dato.replace("A", ":00 A ")
			dato = dato + ":00"
		elif mask == "NN A NN:NN":
			dato = dato.replace(" A", ":00 A")
		elif mask == "NN:NNANN:NN":
			dato = dato.replace("A", " A ")
		elif mask == "NN - NN":
			dato = dato.replace(" - ", ":00 A ")
			dato = dato + ":00"
		elif mask == "NN:NNANN:NN":
			dato = dato.replace("A", " A ")
		elif mask == "NN:NN A NN:N":
			dato = dato + "0"
		elif mask == "NN:N A NN:NN":
			dato = dato.replace(" A", "0 A")
		elif mask == "NNANN A NN:NN":
			dato = dato.replace("A", ":")
			dato = dato.replace(" : ", " A ")
		elif mask == "NN NN":
			dato = dato.replace(" ", ":00 A ")
			dato = dato + ":00"
		elif mask == "NN:NNA N:NN":
			dato = dato.replace("A ", " A 0")
		elif mask == "NN:NN A N:NNN":
			dato = dato[:-1]
			dato = dato.replace("A ", "A 0")
		elif mask == "NNANN NN A NN":
			dato = dato[:2] + ":00 A " + dato.split(" A ")[1] + ":00"
		elif mask == "NN:NN-NNNN-NN":
			rangos = dato.split("-")[2]
			dato = dato[:5] + " A " + rangos + ":00"
		elif mask == "NN:NNAN:NN":
			dato = dato.replace("A", " A 0")
		elif mask == "NN:NN A: NN:NN":
			dato = dato.replace("A:", "A")
		elif mask == "NN:NN ANN:NN":
			dato = dato.replace("A", "A ")
		elif mask == "NN:NN N:NN":
			dato = dato.replace(" ", " A 0")
		elif mask == "NN: A NN":
			dato = dato.replace(":", ":00")
			dato = dato + ":00"
		elif mask == "NN- NN NN-NN":
			dato = dato[:2] + ":00 A " + dato.split("-")[2] + ":00"
		elif mask == "NN-NN NNN-NN":
			dato = dato[:2] + ":00 A " + dato.split("-")[2] + ":00"
		elif mask == "NNANN NN:NN":
			dato = dato.split()[0]
			dato = dato.replace("A", ":00 A ")
			dato = dato + ":00"
		elif mask == "NN-N:NN N-N":
			dato = dato[:2] + ":00 A 0" + dato[-1] + ":00"
		elif mask == "NN-N NN-NN":
			dato = dato[:2] + ":00 A " + dato[-2:] + ":00"
		elif mask == "NN A NN NNANN":
			dato = dato[:2] + ":00 A " + dato[-2:] + ":00"
		elif mask == "NN A N:NN":
			dato = dato.replace(" A ", ":00 A 0")
		elif mask == "NN A NAN:NN A N":
			dato = dato[:2] + ":00 A 0" + dato[-1] + ":00"
		elif mask == "NN:NNAN::N:A:N":
			dato = dato[:5] + " A 0" + dato[-1] + ":00"
		elif mask == "NN:NNAN: N:A:N":
			dato = dato[:5] + " A 0" + dato[-1] + ":00"
		elif mask == "NN:NN:A:NN:A:N":
			dato = dato[:5] + " A 0" + dato[-1] + ":00"
		elif mask == "NN:NN:AN:N:A:N":
			dato = dato[:5] + " A 0" + dato[-1] + ":00"
		elif mask == "NN:NN NNANN:N":
			dato = dato.split()[1]
			dato = dato.replace("A", ":00 A ")
			dato = dato + "0"
		elif mask == "NN:NN NNANN":
			dato = dato.split()[1]
			dato = dato.replace("A", ":00 A ")
			dato = dato + ":00"
		elif mask == "NN:NN A NN:ANN":
			dato = dato.replace("A", "").replace("  ", " A ")
		elif mask == "NN:NN A NN:NNNN":
			dato = dato[:-2]
		elif mask == "NN:NN A NN:NNN":
			dato = dato[:-1]
		elif mask == "NN:NN A NNNN":
			dato = dato[:10]	+ ":" + dato[10:]
		elif mask == "NN:NN ANNANN":
			dato = dato.replace("A", ":")
			dato = dato.replace(" :", " A ")
		elif mask == "NN:N A NN:N":
			dato = dato.replace(" A ", "0 A ")
			dato = dato + "0"
		elif mask == "NN-NN N-N":
			rangos = dato.split("-")
			dato = rangos[0] + ":00 A 0" + rangos[-1] + ":00"
		elif mask == "NNA NN NN A NN" or mask == "NNANN NNANN" or mask == "NNAN NNA NN":
			dato = dato[:2] + ":00 A " + dato[-2:] + ":00"
		elif mask == "NN: A N":
			dato = dato.replace(": A ", ":00 A 0") + ":00"
		elif mask == "NN:A:NN NN:A:NN":
			dato = dato.split()[0].replace(":A:", ":00 A ") + ":00"
		elif mask == "NN:A NN:NN":
			dato = dato.replace(":A ", ":00 A ")
		elif mask == "NN::NN A NN:NN":
			dato = dato.replace("::", ":")
		elif mask == "NN: A NN:NN":
			dato = dato.replace(": ", ":00 ")
		elif mask == "NN: NN A NN:NN":
			dato = dato.replace(": ", ":")
		elif mask == "NN: NN A N:NN":
			dato = dato.replace(": ", ":")
			dato = dato.replace(" A ", " A 0")
		elif mask == "NN:NN-NN NN-NN":
			dato = dato.split()[0].replace("-", " A ") + ":00"
		elif mask == "NN:NN-N N-N":
			dato = dato.split()[0].replace("-", " A 0") + ":00"
		elif mask == "NN:NNANNNN NN":
			dato = dato.split()[0]
			dato = dato[:8] + ":" + dato[8:]
			dato = dato.replace("A", " A ")
		elif mask == "NN:NN ANN":
			dato = dato.replace(" A", " A ") + ":00"
		elif mask == "NN:N A NNANN":
			dato = dato.replace("A", ":").replace(" : ", "0 A ")
		elif mask == "NN-NN NN-:NN" or mask == "NN-NN NN:NN-N":
			dato = dato.split()[0]
			dato = dato.replace("-", ":00 A ") + ":00"
		elif mask == "NN:A:N::N:A:N" or mask == "NN:A N N A N":
			dato = dato[:2] + ":00 A 0" + dato[-1] + ":00"
		elif mask == "NN:: A NN:NN":
			dato = dato.replace("::", ":00")
		elif mask == "NNA:NN A NN:NN":
			dato = dato.replace("A:", ":")
		elif mask == "NNA A NN:NN":
			dato = dato.replace("A A ", ":00 A ")
		elif mask == "NN-NN- NN-NN":
			dato = dato.split()[1]
			dato = dato.replace("-", ":00 A ") + ":00"
		elif mask == "NNANN":
			dato = dato.replace("A", ":00 A ") + ":00"
		elif mask == "NN-NNN NN-NN":
			dato = dato.split()[1]
			dato = dato.replace("-", ":00 A ") + ":00"
		elif mask == "NN-NN NN-NN:N":
			dato = dato + "0"
			dato = dato[:2] + ":00 A " + dato[-5:]
		elif mask == "NN-NN NN -NN" or mask == "NNANN NN NN":
			dato = dato[:2] + ":00 A " + dato [-2:] + ":00"
		elif mask == "NN-NN N-NN:NN":
			dato = dato[:2] + ":00 A " + dato[-5:]
		elif mask == "NNANN N A N" or mask == "NN-NN:NN NN-N":
			dato = dato[:2] + ":00 A 0" + dato[-1] + ":00"
		elif mask == "NNANN NN":
			dato = dato.split()[0]
			dato = dato.replace("A", ":00 A ") + ":00"
		elif mask == "NN-N":
			dato = dato.replace("-", ":00 A 0") + ":00"
		elif mask == "NN-N:NN":
			dato = dato.replace("-", ":00 A 0")
		elif mask == "NN-N N-N":
			dato = dato.split()[0]
			dato = dato.replace("-", ":00 A 0") + ":00"
		elif mask == "NNAN:NN N A N":
			dato = dato[:2] + ":00 A 0" + dato[-1] + ":00"
		elif mask == "NN-N NN-NN:NN":
			dato = dato[:2] + ":00 A " + dato[-5:]
		elif mask == "NN-N A NN-NN":
			dato = dato[:2] + ":00 A " + dato[-2:] + ":00"
		elif mask == "NN-N N-NN:NN":
			dato = dato[:2] + ":00 A " + dato[-5:]
		elif mask == "NNANNA NN:NN":
			dato = dato.replace("A", ":")
			dato = dato.replace(": ", " A ")
		elif mask == "NN-NN ANN-NN":
			dato = dato.replace("-", ":").replace(" A", " A ")
		elif mask == "NNNN A NN":
			dato = dato + ":00"
			dato = dato[:2] + ":" + dato[2:]
		elif mask == "NN AN:NN":
			dato = dato.replace(" A", ":00 A 0")
		elif mask == "NN N":
			dato = dato.replace(" ", ":00 A 0") + ":00"
		elif mask == "NN N:NN":
			dato = dato.replace(" ", ":00 A 0")
		elif mask == "NN A A N":
			dato = dato[:2] + ":00 A 0" + dato[-1] + ":00"
		elif mask == "NN A NNNN":
			dato = dato[:-2] + ":" + dato[-2:]
			dato = dato.replace(" A", ":00 A")
		elif mask == "NN A NNN":
			dato = dato[:-2] + ":" + dato[-2:]
			dato = dato.replace(" A ", ":00 A 0")
		elif mask == "NN A NN NN A NN" or mask == "NN A NN NN ANN" or mask == "NN A NNANN A NN":
			dato = dato[:2] + ":00 A " + dato[-2:] + ":00"
		elif mask == "NN A NN NN NN":
			dato = dato[:7]
			dato = dato.replace(" A ", ":00 A ") + ":00"
		elif mask == "NN A NN N":
			dato = dato[:-2]
			dato = dato.replace(" A ", ":00 A ") + ":00"
		elif mask == "NN A NN NN A NN":
			dato = dato[:2] + ":00 A " + dato[-2:] + ":00"
		elif mask == "NN A N":
			dato = dato.replace(" A ", ":00 A 0") + ":00"
		elif mask == "NN A N N A N":
			dato = dato[:2] + ":00 A 0" + dato[-1] + ":00"
		elif mask == "NN ANN":
			dato = dato.replace(" A", ":00 A ") + ":00"
		elif mask == "NN ANN:N NNANN" or mask == "NN ANN NNANN" or mask == "NN - NN NN-NN":
			dato = dato[:2] + ":00 A " + dato[-2:] + ":00"
		elif mask == "NN -NN":
			dato = dato.replace(" -", ":00 A ") + ":00"
		elif mask == "NN -NN NN-NN" or mask == "NN -NN NN -NN":
			dato = dato[:2] + ":00 A " + dato[-2:] + ":00"
		elif mask == "NN NN NN A NN":
			dato = dato[6:]
			dato = dato.replace(" A", ":00 A") + ":00"
		elif mask == "NN NN A NN NN":
			dato = dato.replace(" ", ":").replace(":A:", " A ")
		elif mask == "N:NN-NN":
			dato = "0" + dato.replace("-", " A ") + ":00"
		elif mask == "N:NN-NN NN-NN":
			dato = "0" + dato[:4] + " A " + dato[-2:] + ":00"
		elif mask == "N:NNA NN:NN":
			dato = "0" + dato.replace("A ", " A ")
		elif mask == "N:NN-NN-NN-NN":
			dato = dato[:7]
			dato = "0" + dato.replace("-", " A ") + ":00"
		elif mask == "N:NNANN NN:NN":
			dato = dato.split()[0]
			dato = "0" + dato.replace("A", " A ") + ":00"
		elif mask == "N:NNANN:NN":
			dato = "0" + dato.replace("A", " A ")
		elif mask == "N:NN-N N-N:NN":
			dato = "0" + dato.split("-")[0] + " A 0" + dato.split("-")[-1]
		elif mask == "N:NN-N:NN-N:NN":
			rangos = dato.split("-")
			dato = "0" + rangos[0] + " A 0" + rangos[1]
		elif mask == "N:NN A ANN:NN":
			dato = "0" + dato.replace(" A A", " A ")
		elif mask == "N:NN A NNANN":
			dato = "0" + dato.replace("A", ":").replace(" : ", " A ")
		elif mask == "N:NN A NN:NN:NN":
			dato = "0" + dato[:-3]
		elif mask == "N:NN A NNANN":
			dato = "0" + dato.replace("A", ":").replace(" : ", " A ")
		elif mask == "N:NN A N":
			dato = "0" + dato + ":00"
			dato = dato.replace("A ", "A 0")
		elif mask == "N:NN NNANN":
			dato = dato.split()[1]
			dato = dato.replace("A", ":00 A ") + ":00"
		elif mask == "N:NN A NNANN":
			dato = "0" + dato.replace("A", ":").replace(" : ", " A ")
		elif mask == "N:NNN A NN:NN":
			dato = "0" + dato[:2] + dato[3:]
		elif mask == "NNN:NN A NN:NN":
			dato = dato[1:]
		elif mask == "NN::NN NN:NN":
			dato = dato.replace("::", ":").replace(" ", " A ")
		elif mask == "NN: NN:NN":
			dato = dato.replace(": ", ":00 A ")
		elif mask == "NN:NNNN:NN":
			dato = dato[:5] + " A " + dato[5:]
		elif mask == "NN:NNN A NN:NN":
			dato = dato[:3] + dato[4:]
		elif mask == "NN:NN A NN NN":
			dato = dato.replace(" ", ":").replace(":A:", " A ")
		elif mask == "NN:NN A N":
			dato = dato.replace("A ", "A 0") + ":00"
		elif mask == "NN:NN A NN::NN":
			dato = dato.replace("::", ":")
		elif mask == "NN:NN NN:N":
			dato = dato.replace(" ", " A ") + "0"
		elif mask == "NN:NN NN:NNN":
			dato = dato[:-1].replace(" ", " A ")
		elif mask == "NN:NN NN:NNN":
			dato = dato.split()[0].replace("-", ":00 A ") + ":00"
		elif mask == "NN A NN:NNN":
			dato = dato[:-1].replace(" A", ":00 A")
		elif mask == "NN A NN NN":
			dato = dato[:-3].replace(" A ", ":00 A ") + ":00"
		elif mask == "NN NNNN":
			dato = dato[:5] + ":" + dato[5:]
			dato = dato.replace(" ", ":00 A ")
		elif mask == "N:NNN A NNA:NN":
			dato = "0" + dato.replace("A:", ":")
			dato = dato[:4] + dato[5:]
		elif mask == "N:NNA ANN:NN":
			dato = "0" + dato.replace("A A", " A ")
		elif mask == "N:NNA AN:NN":
			dato = "0" + dato.replace("A A", " A 0")
		elif mask == "N:NNA NNNN":
			dato = "0" + dato[:8] + ":" + dato[8:]
			dato = dato.replace("A ", " A ")
		elif mask == "N:NNA N:NN":
			dato = "0"	+ dato.replace("A ", " A 0")
		elif mask == "N:NNNN:NN":
			dato = "0" + dato[:4] + " A " + dato[4:]
		elif mask == "N:NN:A:N:NN":
			dato = "0" + dato.replace(":A:", " A 0")
		elif mask == "N:NN:A NN:NN":
			dato = "0" + dato.replace(":A", " A")
		elif mask == "N:NN-NN-NN":
			dato = "0" + dato[:4] + " A " + dato[5:]
			dato = dato.replace("-", ":")
		elif mask == "NN-NN NN-NNNN":
			dato = dato.split()[0].replace("-", ":00 A ") + ":00"
		elif mask == "N:NN AA NN:NN":
			dato = "0" + dato.replace("AA", "A")
		elif mask == "N:NN A A NN:NN":
			dato = "0" + dato.replace("A A", "A")
		elif mask == "N:NN A A NN:NN":
			dato = "0" + dato.replace("A :", "A ") + ":00"
		elif mask == "N:NN A :NN:NN":
			dato = "0" + dato.replace("A :", "A ")
		elif mask == "N:NN A NNNN":
			dato = "0" + dato[:9] + ":" + dato[9:]
		elif mask == "N:NN A NNN":
			dato = "0" + dato[:8] + ":" + dato[8:]
			dato = dato.replace("A ", "A 0")
		elif mask == "N:NN A NN:N":
			dato = "0" + dato + "0" 
		elif mask == "N:NN A NN:NNN":
			dato = "0" + dato[:-1] 
		elif mask == "N:NN A NN:NN N":
			dato = "0" + dato[:-2]
		elif mask == "N:NN A NNA:NN":
			dato = "0" + dato.replace("A:", ":")
		elif mask == "N:NN A NN::NN":
			dato = "0" + dato.replace("::", ":")
		elif mask == "N:NN A NN:ANN":
			dato = "0" + dato.replace(":A", ":")
		elif mask == "N:NN A NN: NN":
			dato = "0" + dato.replace(": ", ":")
		elif mask == "N:NN A :NN":
			dato = "0" + dato.replace("A :", "A ") + ":00"
		elif mask == "N:NN A NN NN":
			dato = "0" + dato.replace(" ", ":").replace(":A:", " A ")
		elif mask == "N:NN A NNANN:NN":
			dato = "0" + dato[:-6] + ":00"
		elif mask == "N:NN A NN NN:NN":
			dato = "0" + dato[:-6] + ":00"
		elif mask == "N:NN A NAN:NN":
			dato = "0" + dato[:-5] + ":00"

		mask = get_mask(dato)
		masks.append(mask)
		lista.append(1)

		return dato


	df[col] = df[col].apply(lambda x: format(x))
	sabana[col]["Máscara Origen"] = masks_origen
	sabana[col]["Máscara"] = masks
	

	lista = []
	return df 
