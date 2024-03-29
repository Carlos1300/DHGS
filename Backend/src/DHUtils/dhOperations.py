from ast import main
from numpy import AxisError, DataSource
from pandas.core.frame import DataFrame
from DHUtils import dhRepository as dhRep
import json
import pandas as pd
from DHUtils import dhLogs as log
from bson.objectid import ObjectId
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
from bson.objectid import ObjectId
import time
from fuzzywuzzy import fuzz

pd.set_option('display.float_format', lambda x: '%.2f' % x)

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
    MONGO_BYTES = 16793598
    byte_size = dhUtilities.get_byte_size(datasources['_main_ds'], mainParams['encoding'])
    
    if datasources['chunks'] > 1:
        df_chunks = dhUtilities.chunk_partitioning_save(datasources['_main_ds'], datasources['chunks'])
        dhRep.delete_chunk_data(stepdict['collection'])
        for chunk in df_chunks:
            doc = json.loads(chunk.to_json(orient='table'))
            dhRep.InsertarDocumentoBDProyecto (stepdict['collection'], doc)
        return True, datasources['_main_ds']
    
    elif byte_size > MONGO_BYTES:
        df_chunks = dhUtilities.chunk_partitioning(byte_size, datasources['_main_ds'])
        dhRep.delete_chunk_data(stepdict['collection'])
        for chunk in df_chunks:
            doc = json.loads(chunk.to_json(orient='table'))
            dhRep.InsertarDocumentoBDProyecto (stepdict['collection'], doc)
        return True, datasources['_main_ds']
    
    else:
        doc =  json.loads(datasources['_main_ds'].to_json(orient='table'))
        doc['_id'] = ObjectId(mainParams['source_id'])
        dhRep.delete_chunk_data(stepdict['collection'])
        dhRep.InsertarDocumentoBDProyecto (stepdict['collection'], doc)
        return True, datasources['_main_ds']

def apply_synonymous(datasources, mainParams, stepdict = None):
    #operacion para aplicar sustitución por sinónimos a una columna origen y coloca el resultado en la columna destino
    dtFrDatos = datasources['_main_ds']
    columna_fuente = stepdict['column_src_appsyno']
    
    filtro = {'RuleName': stepdict['rule_name']}

    ReglasDict = dhRep.obtener_atributos_por_filtro_prj('Rules', filtro, ['data'])[0]['data']

    for regla in ReglasDict:
        dtFrDatos[columna_fuente] = dtFrDatos[columna_fuente].str.replace(regla['search_value'], regla['change_value'])

    log.registrar_ejecucion_exitosa_operacion_dataflow_prj (mainParams['flow_id'], stepdict )
    return True, None

def validate_sourcecolumns_vs_layout (datasources, mainParams, stepdict = None):
    mapeoColumnas = dict()
    dtFrDatos = datasources['_main_ds']
    
    layout = dhRep.BuscarDocumentoBDProyecto('Layouts', 'LayoutName' , stepdict['layout_name_validate'])

    for col in layout['data']:
        if layout['Header']==True:
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
        datasources['_main_layout'] = layout['data']
    else:
        nombres_columnas_error = ''
        for col in mapeoColumnas:
            for column_name in mapeoColumnas:
                nombres_columnas_error += column_name + ', ' if mapeoColumnas[column_name] == '' else ''
        stepdict['execute_status'] = 'Ejecution.ERROR'
        stepdict['execute_error_text'] = 'La fuente no cumple con las columnas especificadas en el Layout ' + layout['name'] + ': '+ nombres_columnas_error

    return mapeoOk, layout

def extract_layout_from_source (datasources, mainParams, stepdict = None):
    
    dtFrDatos = datasources['_main_ds']
    
    if '_main_layout' not in datasources.keys():
        validacion, layout = validate_sourcecolumns_vs_layout (datasources, mainParams, stepdict)
        if validacion == False:
            return False, None
    
    layout = datasources['_main_layout']
    nombresColumnas =  [ column['column_name_source'] for column in layout]
    dtFrDatos = pd.DataFrame( dtFrDatos[ nombresColumnas] )
    dtFrDatos.rename (columns={ column['column_name_source'] : column['column_name'] for column in layout }, inplace=True)
    datasources['_main_ds'] = dtFrDatos

    return True, dtFrDatos

def validate_vs_layout_datatypes (datasources, mainParams, stepdict = None):
    
    dtFrDatos = datasources['_main_ds']
    
    if '_main_layout' not in datasources.keys():
        validacion, layout = validate_sourcecolumns_vs_layout (datasources, mainParams, stepdict)
        if validacion == False:
            return False, None
    
    layout = datasources['_main_layout']
    for col in layout:
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
    nombre_columna = stepdict['column_src_valnr']


    dtfNoValidos=dtFrDatos[nombre_columna].copy()
    dtfNoValidos[:] = False

    filtro={ 'RuleName' : stepdict['rule_name_valnr'] }
    ReglasDict = dhRep.obtener_atributos_por_filtro_prj('Rules', filtro, ['data'])[0]['data']

    for regla in ReglasDict:
        Minimo = regla['min_value']
        Maximo = regla['max_value']
        dtfNoValidos = (dtFrDatos[nombre_columna] < Minimo) | dtfNoValidos
        dtfNoValidos = (dtFrDatos[nombre_columna] > Maximo) | dtfNoValidos

    dtfNoValidos = ['R' if x == False else 'OR' for x in dtfNoValidos]
    
    dtFrDatos[stepdict['column_src_valnr'] + '_numeric_range'] = dtfNoValidos

    return True, dtFrDatos

def validate_exist_in_catalog (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    dictObj = dhRep.BuscarCatalogoEnBD('Catalogos', 'CatalogName', stepdict['catalog_name_excat'])
    valores_catalogo = pd.read_json(json.dumps(dictObj), orient='table')
    valores_fuente = dtFrDatos[stepdict['column_src_excat']].to_list()
    valores_catalogo = valores_catalogo[stepdict['key_column_name_excat']].to_list()

    dtFrDatos['exist_catalog'] = ['E' if valor in valores_catalogo else 'NE' for valor in valores_fuente]

    return True, None

def apply_join_from_value_vs_catalog (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    dictObj = dhRep.BuscarCatalogoEnBD('Catalogos', 'CatalogName', stepdict['catalog_name_joincat'])
    valores_catalogo = pd.read_json(json.dumps(dictObj), orient='table')
    dtt = valores_catalogo.set_index(stepdict['key_column_name_joincat'])
    dataJoin = dtFrDatos.join(dtt, on=stepdict['column_src_joincat'], rsuffix='_B' )
    dtFrDatos[stepdict['column_dest_joincat']] = dataJoin[stepdict['value_column_name_joincat']]
    return  True, None

def apply_mask (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    fmt = stepdict['mask_string_apply']
    dtFrDatos[stepdict['column_dest_appmk']]  = [fmt.format( valor ) for valor in  dtFrDatos[ stepdict['column_src_appmk']]]
    return True, None

def extract_mask_from_text (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    mascara = '(' + stepdict['mask_string_extract'] + ')'
    dtFrDatos[stepdict['column_dest_exmk']] = dtFrDatos[stepdict['column_src_exmk']].str.extract(r''+mascara, expand=False)
    return True, None

def extract_words_by_position (datasources, mainParams, stepdict = None):
    dtFrDatos = datasources['_main_ds']
    re_Delimitador = '\\' + stepdict['separator_exwrd']
    ini = stepdict['init_position_exwrd']
    fin = stepdict['final_position_exwrd']
    clCount = dtFrDatos[stepdict['column_src_exwrd']].str.count(re_Delimitador).fillna(0).astype(int) + 1
    nMaxSep = clCount.max().astype(int) - 1

    def fnConcat (arr, ini, fin, sep):
        x = ''
        fin =  (fin if len(fin) < len(arr) else len(arr))+1
        for i in range(ini, fin):
            x+= arr[i] + sep
        return x

    ser_Valores = dtFrDatos[stepdict['column_src_exwrd']].str.split(re_Delimitador)
    dtFrDatos[stepdict['column_dest_exwrd']] = ser_Valores.apply(lambda arr: fnConcat(arr,ini,fin, stepdict['separator_exwrd'])  )

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
    origen = stepdict['col_origen_valfon']
    df_main = datasources['_main_ds']
    
    def assign_values(x):
        if x in count_dict.keys():
            x = count_dict[x]
        return x
    
    result = pd.DataFrame()
    result[origen] = df_main[origen]
    result["soundex"] = result[origen].apply(lambda x: jellyfish.soundex(x))
    
    count = [result['soundex'].str.contains(x).sum() for x in result['soundex'].unique()]
    count_vals = list(zip(result['soundex'].unique(), count))
    count_dict = {key: value for (key, value) in count_vals}
    
    result['freq soundex'] = result['soundex'].apply(
    lambda x: assign_values(x)
    )
    
    result["soundex dist%"] = (result["freq soundex"] / len(df_main.index))*100
    result["metaphone"] = result[origen].apply(lambda x: jellyfish.metaphone(x))
    
    count = [result['metaphone'].str.contains(x).sum() for x in result['metaphone'].unique()]
    count_vals = list(zip(result['metaphone'].unique(), count))
    count_dict = {key: value for (key, value) in count_vals}
    
    result['freq metaphone'] = result['metaphone'].apply(
    lambda x: assign_values(x)
    )
    
    result["metaphone dist%"] = (result["freq metaphone"] / len(df_main.index))*100
    result.drop_duplicates(inplace=True)
    
    doc = json.loads(result.to_json(orient='table'))
    doc['name'] = "Foneticos - " + origen
    
    fon = dhRep.BuscarDocumentoBDProyecto('DataPerf', 'name', 'Foneticos - ' + origen)
    if fon == None: 
        dhRep.InsertarDocumentoBDProyecto ("DataPerf", doc)
        return True, result
    else:
        return True, fon['_id']


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
    value_1 = stepdict['value_1_calcexp']
    value_2 = stepdict['value_2_calcexp']
    dest = stepdict['col_dest_calcexp']
    oper = stepdict['operator_calcexp']
    
    if df_main[value_1].dtype.name == "object" or df_main[value_2].dtype.name == "object":
        return False, df_main

    ops = {'+' : operator.add, '-' : operator.sub, '*' : operator.mul, '/' : operator.truediv, }
    df_main[dest] = df_main.apply(lambda row : ops[oper](float(row[value_1]), float(row[value_2])), axis=1)
    return True, df_main

def create_mask(datasources, mainParams, stepdict = None):
    src = stepdict['column_src_crmk']
    dest = stepdict['column_dest_crmk']
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
                mask += str(c).upper()
        return mask
    result = datasources['_main_ds']
    result[dest] = result[src].apply(
    lambda dato: get_mask(str(dato))
    )
    return (True, result)

def get_value_freq(datasources, mainParams, stepdict = None):
    df_main = datasources['_main_ds']
    col_src = stepdict['column_src_fqval']
    col_id = int(stepdict['column_id_fqval'])
    separator = stepdict['separator_fqval']
    one_word = stepdict['one_word_fqval']
    init_pos = int(stepdict['init_pos_fqval'])
    
    final_pos = None if int(stepdict['final_pos_fqval']) == "None" else int(stepdict['final_pos_fqval'])
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
                
    def assign_values(x):
        if x in count_dict.keys():
            x = count_dict[x]
        return x
                
    df_main.apply(lambda row: iterate_words(row), axis=1)
    df_final = pd.DataFrame({
        'Phrase' : new_column,
        'Id' : ids, 
    })
    df_final['Words'] = df_final['Phrase'].apply(
        lambda x: len(x.split(separator))
    )
    
    count = [df_final['Phrase'].str.contains(x).sum() for x in df_final['Phrase'].unique()]
    count_vals = list(zip(df_final['Phrase'].unique(), count))
    count_dict = {key: value for (key, value) in count_vals}
    
    df_final['Frequency'] = df_final['Phrase'].apply(
        lambda x: assign_values(x)
    )
    df_final['Dst %'] = round(((df_final['Frequency'] / df_final.shape[0])*100), 3)
    df_final["Category"] = ""
    df_final.drop_duplicates(inplace=True)
    
    doc = json.loads(df_final.to_json(orient='table'))
    doc['name'] = "Frequency - " + col_src
    
    freq = dhRep.BuscarDocumentoBDProyecto('DataPerf', 'name', 'Frequency - ' + col_src)
    if freq == None: 
        dhRep.InsertarDocumentoBDProyecto ("DataPerf", doc)
        return True, df_final
    else:
        return True, freq['_id']

def clean_html(datasources, mainParams, stepdict = None):
    #Se leen los valores de los parámetros.
    df_main = datasources['_main_ds']
    origen = stepdict['col_origen_clhtml']
    destino = stepdict['col_destino_clhtml']
    chr_especiales  = stepdict['chr_especiales_clhtml']
    salto = stepdict['salto_linea_clhtml']
    titulos_img = stepdict['titulos_img_clhtml']

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
        
        null_count = int(dataframe[col].isna().sum())
            
        col_info = {
            "Data Type" : col_type,
			"Max Length" : max_len,
			"Max Value" : max_val,
			"Min Length" : min_len,
			"Min Value" : min_val,
			"Nulls" : has_nulls,
			"Null Count": null_count
            }
        
        data_info[col] = col_info
        
    
    doc = json.loads(json.dumps(data_info))
    doc['name'] = "Data Summary"
    
    summary = dhRep.BuscarDocumentoBDProyecto('DataPerf', 'name', 'Data Summary')
    
    if summary == None:
        dhRep.InsertarDocumentoBDProyecto ("DataPerf", doc)
        return True, col_info
    else:
        dhRep.EliminarDocumentoProyecto('DataPerf', summary)
        dhRep.InsertarDocumentoBDProyecto ("DataPerf", doc)
        return True, summary['_id']
    
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
    origen = stepdict['col_origen_substring']
    destino = stepdict['col_destino_substring']
    init_word = int(stepdict['init_word_substring'])
    total_words = int(stepdict['total_words_substring'])
    sep = str(stepdict['separator_substring'])
    join_char = str(stepdict['join_char_substring'])

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
    origen = [x.strip() for x in stepdict['col_origen_concatcols'].split(',')]
    dest = stepdict["col_destino_concatcols"]
    join_char = stepdict["join_char_concatcols"]
    df_main[dest] = df_main[origen].apply(lambda row: join_char.join(row.values.astype(str)), axis=1)
    return True, df_main


########## FUNCIONES DE EDENRED ADAPTADAS AL DATAHUB ##########


def adjust_length(datasources, mainParams, stepdict= None):
    """Método encargado de ajustar las columnas a la longitud deseada.

    Args:
        datasources (_type_): _description_
        mainParams (_type_): _description_
        stepdict (_type_, optional): _description_. Defaults to None.
    """

    def check_len(dato):
        dato = str(dato)
        if len(dato) >= length:
            dato = ''.join(list(dato)[:length])
        elif len(dato) < length:
            dato = dato + "0"*(length - len(dato))
        
        return dato

    df_main = datasources['_main_ds']
    columns = [x.strip() for x in stepdict['apply_cols_adjlen'].split(',')]
    length = int(stepdict['length_adj'])
    
    for column in columns:
        df_main[column] = df_main[column].apply(lambda x: check_len(x))
        
    return True, df_main

def rm_negativos(datasources, mainParams, stepdict= None):
	'''
	Método que elimina números negativos de una columna numerica.
	'''

	def check(dato):
		dato = str(dato)
		if dato != "" and dato[0] == "-":
			dato = ""
		else:
			dato = dato
		return dato

	df_main = datasources['_main_ds']

	columns = [x.strip() for x in stepdict['apply_cols_rmne'].split(',')]
 
	for col in columns:
		df_main[col] = df_main[col].apply(lambda x: check(x))
 
	return True, df_main

def upper_col(datasources, mainParams, stepdict= None):
	"""
	Método que elimina pone en mayusculas los dato de una serie de columnas.
	:param df: DataFrame a utilizar.
	:param columns: Lista de columnas donde se aplica la rutina.
	"""

	def upper_data(dato):
		dato = str(dato)
		if not dato.isupper() and not dato.isnumeric() and dato != "" and dato != "NAN" and dato != "nan":
			dato = dato.upper()
		else:
			dato = dato
		return dato

	df_main = datasources['_main_ds']

	columns = [x.strip() for x in stepdict['apply_cols_upcol'].split(',')]
	for col in columns:
		df_main[col] = df_main[col].apply(lambda x: upper_data(x))

	return True, df_main

def lower_col(datasources, mainParams, stepdict= None):
	"""
	Método que elimina pone en minúsculas los dato de una serie de columnas.
	:param df: DataFrame a utilizar.
	:param columns: Lista de columnas donde se aplica la rutina.
	"""

	def lower_data(dato):
		dato = str(dato)
		if not dato.islower() and not dato.isnumeric() and dato != "" and dato != "NAN" and dato != "nan":
			dato = dato.lower()
		else:
			dato = dato
		return dato

	df_main = datasources['_main_ds']

	columns = [x.strip() for x in stepdict['apply_cols_locol'].split(',')]
 
	for col in columns:
		df_main[col] = df_main[col].apply(lambda x: lower_data(x))

	return True, df_main

def num_to_bool(datasources, mainParams, stepdict= None):
	"""
	Método reemplaza valores numericos (0, 1) por valores booleanos.
	Args:
		df (DataFrame): DataFrame a utilizar.
		columns (Lista): Lista de columnas en donde se aplica la regla.
	Returns:
		Retorna el DataFrame modificado. 
	"""

	def transform(dato):
		if int(dato) == 1:
			dato = True
		elif int(dato) == 0:
			dato = False
		return dato

	df_main = datasources['_main_ds']

	columns = [x.strip() for x in stepdict['apply_cols_nubo'].split(',')]

	for col in columns:
		df_main[col] = df_main[col].apply(lambda x: transform(x))

	return True, df_main

def trim_col(datasources, mainParams, stepdict= None):
    
    def rm_blanks(dato):
        dato = str(dato)
        if stepdict['all'].lower() == 'no':
            if dato.count(" ") >= len(dato.split()):
                dato = dato.strip()
                dato = re.sub(' +', " ", dato)
        else:
            if dato.count(" ") >= 1:
                dato = re.sub(re.compile(r'\s+'), '', dato)
        return dato
    
    df_main = datasources['_main_ds']
    
    columns = [x.strip() for x in stepdict['apply_cols_trim'].split(',')]
    
    for col in columns:
        df_main[col] = df_main[col].apply(lambda x: rm_blanks(x))
    
    return True, df_main

def replace_char_exc(datasources, mainParams, stepdict= None):
    
    def rep(dato):
        dato = str(dato)
        exc = [x.strip() for x in stepdict['excluded_chars'].split(',')]
        
        if not dato == "" and str(dato[0]).isalpha():
            dato = dato.replace(dato[0], stepdict['replace_char'])
        for c in dato:
            if c.isalpha() and not c in exc:
                dato = dato.replace(c, stepdict['replace_char'])
        return dato
    
    df_main = datasources['_main_ds']
    
    columns = [x.strip() for x in stepdict['apply_cols_reexchar'].split(',')]
    
    for col in columns:
        df_main[col] = df_main[col].apply(lambda x: rep(x))
        
    return True, df_main

def rm_accents(datasources, mainParams, stepdict= None):
    
    def accents(dato):
        dato = str(dato)
        rm_dato = unidecode.unidecode(dato)
        
        return rm_dato
    
    df_main = datasources['_main_ds']
    
    columns = [x.strip() for x in stepdict['apply_cols_rmacc'].split(',')]
    
    for col in columns:
        df_main[col] = df_main[col].apply(lambda x: accents(x))
    
    return True, df_main

def check_email(datasources, mainParams, stepdict= None):
    
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
        
        if not (re.fullmatch(regex, dato)):
            valid_mail.append('NV')
        else:
            valid_mail.append('V')
        
        return dato

    df_main = datasources['_main_ds']
    
    valid_mail = []
    
    columns = [x.strip() for x in stepdict['apply_cols_cheml'].split(',')]
    
    for col in columns:
        df_main[col] = df_main[col].apply(lambda x: check(x))
        df_main[col + '_valid_mail'] = valid_mail
    
    return True, df_main

def replace_char(datasources, mainParams, stepdict= None):
    
    def rep(dato):
        dato = str(dato)
        values = [x.strip() for x in stepdict['rep_char_values'].split(',')]
        for value in values:
            if value in dato:
                dato = dato.replace(value, stepdict['rep_value'])
        return dato
    
    df_main = datasources['_main_ds']
    
    columns = [x.strip() for x in stepdict['apply_cols_rechar'].split(',')]
    
    for col in columns:
        df_main[col] = df_main[col].apply(lambda x: rep(x))
        
    return True, df_main

def windowKey(datasources, mainParams, stepdict=None):

    cols = [x.strip() for x in stepdict['windowkey_cols'].split(',')]
    methods = [x.strip() for x in stepdict['windowkey_methods'].split(',')]
    df_main = datasources['_main_ds']

    windowKey = []

    col_methods = {col: method for (col, method) in zip(cols, methods)}

    for col in col_methods.keys():
        if stepdict["wk_upper"].lower() != 'no':
            if col_methods[col] == 'sub':
                windowKey.append(list(map(lambda x : unidecode.unidecode(x[:int(stepdict["wk_sub_length"])].replace(' ', '').upper()), df_main[col].astype('string'))))
            else:
                windowKey.append(list(map(lambda x : jellyfish.soundex(unidecode.unidecode(x)).upper(), df_main[col].astype('string'))))
        else:
            if col_methods[col] == 'sub':
                windowKey.append(list(map(lambda x : unidecode.unidecode(x[:int(stepdict["wk_sub_length"])].replace(' ', '').lower()), df_main[col].astype('string'))))
            else:
                windowKey.append(list(map(lambda x : jellyfish.soundex(unidecode.unidecode(x)).lower(), df_main[col].astype('string'))))

    df_main["windowKey"] = list(map(''.join, zip(*windowKey)))
    df_main.sort_values('windowKey', inplace=True)
    
    return True, df_main


def matcher(datasources, mainParams, stepdict=None):

    def exact_match(str1, str2):
        if str1 == str2:
            return 1
        else:
            return 0
        
    cols = [x.strip() for x in stepdict['matcher_cols'].split(',')]
    methods = [x.strip() for x in stepdict['matcher_methods'].split(',')]
    df_main = datasources['_main_ds']

    g = df_main.groupby("windowKey")
    sims = []
    dup_flags = []

    for group, data in g:
        results = []
        g_length = data.shape[0]

        
        if data.shape[0] == 1:
            sims.append([-1])
        
        else:
            vals = {i : {} for i in range(len(cols))}
            for i in range(len(cols)):
                vals[i]["col"] = cols[i]
                vals[i]["values"] = data[cols[i]].values
                vals[i]["method"] = methods[i]

            for i in range(len(vals.keys())):
                for j in range(len(vals[i]["values"])):
                    res= []
                    for k in range(len(vals[i]["values"])):
                        match vals[i]["method"]:
                            case 'E':
                                res.append(exact_match(str(vals[i]["values"][j]), str(vals[i]["values"][k])))
                            case 'J':
                                res.append(jellyfish.jaro_winkler_similarity(str(vals[i]["values"][j]), str(vals[i]["values"][k])))
                            case 'F':
                                res.append(fuzz.ratio(str(vals[i]["values"][j]), str(vals[i]["values"][k]))/100)
                    results.append(res)
            s = list(map(lambda *res : round((sum(res) / len(vals.keys()))/ g_length, 2) * 100, *results))
            first = True

            for element in s:
                if element >= stepdict["upper_bound"] and first:
                    dup_flags.append(1)
                    first = False
                elif element < stepdict["upper_bound"]:
                    dup_flags.append(1)
                else:
                    dup_flags.append(0)
            
            sims.append(s)
        
    flat_list = [item for sublist in sims for item in sublist]
    df_main["Similarity %"] = flat_list
    df_main["Unique"] = [1 if x < int(stepdict["lower_bound"]) else 0 for x in df_main["Similarity %"]]
    df_main["Suspicious"] = [1 if int(stepdict["lower_bound"]) <= x < int(stepdict["upper_bound"]) else 0 for x in df_main["Similarity %"]]
    df_main["Duplicate"] = [1 if x >= int(stepdict["upper_bound"]) else 0 for x in df_main["Similarity %"]]
    df_main["Dup Flag"] = dup_flags

    return True, df_main