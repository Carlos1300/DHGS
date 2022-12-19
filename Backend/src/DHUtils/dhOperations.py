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

## Todas las operaciones deben establecer el valor del diccionario '' a True o false
## OperaciónCorrecta = {Falso|Verdadero}
##

def load_source_main (datasources, mainParams, stepdict = None ):
    # _main_ds siempre hará referencia a la fuente de datos original donde se estará trabajando
    
    """
    Función para cargar los datos base o main que se utilizarán.
    
    """
    
    dictObj = dhRep.obtener_atributos_por_docid_prj('DataLoads', mainParams['source_id'], ['schema','data'] )
    datasources['_main_ds'] = pd.read_json(StringIO(json.dumps(dictObj)), orient='table')
    return True, datasources['_main_ds']

def save_source_main (datasources, mainParams, stepdict = None ):
    
    """
    Función para guardar los datos base o main que se utilizarán.
    
    """
    
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

def window_key(datasources, mainParams, stepdict = None):
    dataframe = datasources['_main_ds']
    dataframe["window_key"]=""
    vocales = "AEIOUaeiou"
    consonantes = "bcdfghjklmnpqrstwxyzñ"
    consonantes = consonantes + consonantes.upper()

    #Funnción que obtiene las vocales de un dato.
    def get_vowels(dato, rango, repetir = True, actual=''):
        res = actual
        for c in dato[0:None]:
            if (len(res) == rango):
                    return res
            if c in vocales:
                if (not repetir and c not in res):
                    res += c
                if (repetir):
                    res += c 
        return res

    #Funnción que obtiene las consonantes de un dato.
    def get_consonants(dato, rango, repetir = True, actual=''):
        res = actual
        for c in dato[0:None]:
            if (len(res) == rango):
                    return res
            if c in consonantes:
                if (not repetir and c not in res):
                    res += c
                if (repetir):
                    res += c
        return res 

    #Función que obtiene cualquier caractér de un dato en un rango especificado.
    def get_any(dato, rango, repetir = True, actual=''):
        res = actual
        for c in dato[0:None]:
            if (len(res) == rango):
                return res
            if (not repetir and c not in res):
                res += c
            if (repetir):
                res += c
        return res  

    #Se obtienen los valores de los diccionarios
    columnas = stepdict.get('columnas')
    reglas = stepdict.get('reglas')
    rangos = stepdict.get('rangos')
    repetidos = stepdict.get('repetir')

    #Se valida que la longitud de las listas de parámetros sea la misma.
    is_valid = len(columnas) == len(reglas) and len(reglas) == len(rangos) and len(rangos) == len(repetidos)
    #En caso de que no, se regresa False y el dataframe sin llaves.
    if not is_valid:
        return False, dataframe

    #Se recorre cada parámetro por regla
    for x in range(len(columnas)):
        columna = columnas[x]
        selection = reglas[x]
        rango = rangos[x]
        repetir = repetidos[x]
        
        #Vocales
        if ("A" == selection):
            dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
                lambda x: get_any(x, rango, repetir = repetir)
                ) 
        elif ("V" == selection):
            dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(lambda x: get_vowels(x,rango, repetir = repetir))
        elif ("FV" == selection):
            dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
                lambda x: get_vowels(x[1:], rango, actual=x[0], repetir=repetir)
                ) 
        elif ("FV2" == selection):
            dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
                lambda x: get_vowels(x[1:], rango, actual=x[0], repetir=repetir)
                ) 

        #Consonantes    
        elif ("C" == selection):
            dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(lambda x: get_consonants(x,rango, repetir = repetir))
            
        elif ("FC" == selection):
            dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
                lambda x: get_consonants(x[1:], rango, actual=x[0], repetir=repetir)
                )

        elif ("FC2" == selection):
            dataframe['window_key'] = dataframe['window_key'] + dataframe[columna].apply(
                lambda x: get_consonants(x[1:], rango,  actual=x[0], repetir=repetir)
                ) 
    return True, dataframe

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
    init_word = stepdict['init_word']
    total_words = stepdict['total_words']
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
    origen = stepdict["cols_origen"]
    dest = stepdict["col_destino"]
    join_char = stepdict["join_char"]
    df_main[dest] = df_main[origen].apply(lambda row: join_char.join(row.values.astype(str)), axis=1)
    return True, df_main

