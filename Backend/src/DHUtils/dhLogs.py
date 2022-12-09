from DHUtils import dhRepository
from datetime import datetime


def RegistrarError_BDProyecto (Entidad, idEntidad, NumeroError, valorError):
    doc = {
        'type': 'ERROR',
        'Entity': Entidad,
        'Entity_ID': idEntidad,
        'Number': NumeroError,
        'Value': valorError,
        'Date': datetime.now()
    }
    dhRepository.InsertarDocumentoBDProyecto('Log_Errors', doc )


def registrar_ejecucion_exitosa_operacion_dataflow_prj ( DataFlow_Id, dhStepDataFlow ):
     doc = {
         'type':'LOG',
         'Entity': 'DataFlow',
         'Entity_ID': DataFlow_Id,
         'Number': 0,
         'Value': dhStepDataFlow['order'],
         'Date': datetime.now()

     }
     dhRepository.InsertarDocumentoBDProyecto('Log_Errors', doc)


def registrar_ejecucion_fallida_operacion_dataflow_prj(DataFlow_Id, dhStepDataFlow):
    doc = {
        'type': 'LOG',
        'Entity': 'DataFlow',
        'Entity_ID': DataFlow_Id,
        'Number': 0,
        'Value': dhStepDataFlow['order'],
        'Error': dhStepDataFlow['execute_error_text'] if 'execute_error_text' in dhStepDataFlow else '',
        'Date': datetime.now()

    }
    dhRepository.InsertarDocumentoBDProyecto('Log_Errors', doc)

