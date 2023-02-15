import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { ProjectContext } from "../context/projectContext";
import LinearProgress from '@mui/material/LinearProgress';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

const API = process.env.REACT_APP_API;

export const DataSummaryTable = () => {

  const [dataSummary, setDataSummary] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const getSummary = async () =>{
    const res = await fetch(API + '/summary/' + localStorage.getItem('project'));
    if(res.status !== 200){
      setDataSummary([]);
      setLoadingTable('disabled');
    }else{
      const data = await res.json();
      setDataSummary(data);
      setLoadingTable('disabled');
    }
  }

  useEffect(() => {
    getSummary()  
  }, [])

  const NoRows = () =>{
    return(
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%"}}>
        <img style={{width: "120", height: "100"}} src="https://static.vecteezy.com/system/resources/thumbnails/010/856/652/small/no-result-data-document-or-file-not-found-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-etc-vector.jpg" alt="No data" />
        <p>No se encontró ningún sumario en este proyecto.</p>
      </div>
    )
  }

  const columns = [
    { field: 'id', hide: true},
    { field: 'Column', headerName: "Columna", width: 190},
    { field: "Data Type", headerName: "Tipo de Dato", width: 110 },
    { field: "Max Length", headerName: "Longitud Máxima", width: 140 },
    { field: "Max Value", headerName: "Valor Máximo", width: 180 },
    { field: "Min Length", headerName: "Longitud Mínima", width: 140 },
    { field: "Min Value", headerName: "Valor Mínimo", width: 180 },
    { field: "Nulls", headerName: "Valores Nulos", width: 130 },
    { field: "Null Count", headerName: "Conteo de Nulos", width: 130 },
  ];

  return(
    <div className="datatable">
      <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
        <Fade in={open}>
          <div className="modalBox">
            <div className="closeBtn" onClick={handleClose}>&times;</div>
            <div className="modalContent">
              <div className="modalTitle">
                  <h3><b>Página de Sumario de Datos</b></h3>
              </div>
              <div className="modalText">
                <p>En esta página podrás encontrar el sumario de datos generado por la regla <b><i>Obtención del tipo de columna</i></b> al ser ejecutada por algún flujo. Cabe destacar que este sumario, a diferencia del resumen, contiene todos los tipos de datos existentes en la fuente de datos.</p>
                <p>A continuación, se presenta un desglose de las columnas contenidas y su significado.</p>
                <div className="modalTable">
                  <table>
                    <thead>
                      <tr>
                          <th style={{width: "20%"}}>Columna</th>
                          <th style={{width: "80%"}}>Descripción</th>
                      </tr>
                    </thead>
                    <tr>
                      <td>Columna</td>
                      <td>Nombre de la columna que será evaluada.</td>
                    </tr>
                    <tr>
                      <td>Tipo de Dato</td>
                      <td>Categoría de dato del lenguaje Python al que pertenece la información de la columna (str, int, float, etc).</td>
                    </tr>
                    <tr>
                      <td>Longitud Máxima</td>
                      <td>Número máximo de caracteres que se encontró en la columna.</td>
                    </tr>
                    <tr>
                      <td>Valor Máximo</td>
                      <td>Valor máximo encontrado en la columna.</td>
                    </tr>
                    <tr>
                      <td>Longitud Mínimo</td>
                      <td>Número mínimo de caracteres que se encontró en la columna.</td>
                    </tr>
                    <tr>
                      <td>Valor Mínimo</td>
                      <td>Valor mínimo encontrado en la columna.</td>
                    </tr>
                    <tr>
                      <td>Valores Nulos</td>
                      <td>Indica la existencia o no de valores nulos en la columna.</td>
                    </tr>
                    <tr>
                      <td>Conteo de Nulos</td>
                      <td>Indica el número de valores nulos encontrados en la columna.</td>
                    </tr>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </Fade>
      </Modal>

      <div className="top">
        <h1 className="title">Sumario de Datos</h1>
        <div className="tableButtons perf">
          <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
        </div>
      </div>
      <div className="table">
        <DataGrid
        rows={dataSummary}
        columns={columns}
        pageSize={9}
        rowsPerPageOptions={[9]}
        disableSelectionOnClick
        components={{
          LoadingOverlay: LinearProgress,
          NoRowsOverlay: NoRows
        }}
        loading={loadingTable === 'enabled' ? true : false}
        />
      </div>
    </div>
  )
}