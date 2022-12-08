# datahub

Backend de la herramienta datahub que permitirá hacer funciones de ETL (Extracción, Transformación y Carga) aplicando rutinas especializadas de limpieza y enriquecimiento de datos.

La herramienta utiliza una BD de datos Mongo para almacenar los datos origen, los datos procesados y la trazabilidad del dato para poder identificar a nivel registro todos los procesos que fueron aplicados al dato. Se eligió Mongo al ser una base de tipo NoSQL ya que permite el dinamismo en nombre y número de columnas a diferencia de una base de datos relacional donde es necesario definir previamente la estructura de cada tabla.

El orden de ejecución de los scripts es:
* DatahubEx.py .- Para leer los datos originales y cargarlos a MongoDB, desde una ubicación local, datalake, carpeta de red o sharepoint.

	Parametros: 

		-pnm : Project Name. El nombre del proyecto, todos los comandos de datahub se ejecutan dentro del contexto de un proyecto

		-src : Source Type. Tipo de archiv que se va a cargar(xlsx, csv)

		-fln : File Name. Nombre del archivo fuente que incluye la ruta

		-sht : Sheet Name. Nombre de la hoja del archivo fuente, aplica solo para archivos de Excel

		-enc : Encoding.  Codificación del archivo de texto ("UTF-8"(default),"ANSI", etc) , aplica solo para archivos de csv.

		-sep : Separator. Separador utilizado en el csv (","(default) ,"|", etc) , aplica solo para archivos de csv.

* DatahubTr.py .- Para ejecutar un dataflow, o secuencia de operaciones a los datos originales. cada operación almacena en la BD Mongo sus resultados y trazabilidad
	
	Parametros:
		
		-pnm : Project Name. El nombre del proyecto, todos los comandos de datahub se ejecutan dentro del contexto de un proyecto.

		-sid : Source ID. ID de la fuente de datos. (Visible en compass).

		-fid : Flow ID. OjectID del flujo de datos que se va a ejecutar (Definido en compass).
	
* DatahubLd.py .- Para Generar un layout de salida y depositarlo en un destino: archivo plano, BD SQL, ubicación en la red, datalake, etc

	Parametros:

		-pnm : Project Name. El nombre del proyecto, todos los comandos de datahub se ejecutan dentro del contexto de un proyecto.

		-sid : Source ID. ID de la fuente de datos. (Visible en compass).

		-opt : Output Type. Tipo de archivo de salida. Ej. csv

		-onm : Output Name. Nombre del archivo a crear.


********************************************************************************************************************************************************************************************************************************
* Ejemplo de flujo de comandos a ejecutar en consola

1)
	py DatahubEx.py -pnm "IDS" -src "csv" -fln "C:\\Users\\intus\\Downloads\\test.csv" -enc "UTF-8" -sep ","

2)
	py DatahubTr.py -pnm "IDS" -sid "62ed8d98df7437da17bf6e95" -fid "62ed8e661450a63050065dc8"

3)
	py DataHubLd.py -pnm "IDS" -sid "62ed8d98df7437da17bf6e95" -otp "csv" -onm "salida - test2"
