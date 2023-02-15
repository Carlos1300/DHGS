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

export const DataPerfTable = () => {

  const [dataPerfs, setDataPerfs] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const getPerfs = async () =>{
    const res = await fetch(API + '/resume/' + localStorage.getItem('project'));
    const data = await res.json();
    setDataPerfs(data);
    setLoadingTable('disabled');
  }

  useEffect(() => {
    getPerfs();
  }, [])

  const NoRows = () =>{
    return(
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%"}}>
        <img style={{width: "120", height: "100"}} src="https://static.vecteezy.com/system/resources/thumbnails/010/856/652/small/no-result-data-document-or-file-not-found-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-etc-vector.jpg" alt="No data" />
        <p>No se encontraró ningún resumen en este proyecto.</p>
      </div>
    )
  }

  const columns = [
    { field: 'id', hide: true},
    { field: 'Column', headerName: "Columna", width: 165},
    { field: "count", headerName: "Registros", width: 100 },
    { field: "max", headerName: "Valor Máximo", width: 130 },
    { field: "min", headerName: "Valor Mínimo", width: 130 },
    { field: "mean", headerName: "Media", width: 140 },
    { field: "std", headerName: "Desviación Estándar", width: 150 },
    { field: "25%", headerName: "Primer Cuartil", width: 130 },
    { field: "50%", headerName: "Segundo Cuartil", width: 130 },
    { field: "75%", headerName: "Tercer Cuartil", width: 130 },
  ];

  return(
      <div className="datatable">
        <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
          <Fade in={open}>
            <div className="modalBox">
              <div className="closeBtn" onClick={handleClose}>&times;</div>
              <div className="modalContent">
                <div className="modalTitle">
                    <h3><b>Página de Resumen de Datos</b></h3>
                </div>
                <div className="modalText">
                  <p>En esta página podrás encontrar el resumen estadístico de los datos generado por el DataHub al momento de añadir una nueva fuente de datos. Cabe destacar que este resumen solo contiene la información estadística de aquellas variables que sean del tipo entero (int) o decimal (float).</p>
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
                        <td>Nombre de la columna encontrada en la fuente de datos con tipos de dato entero o decimal.</td>
                      </tr>
                      <tr>
                        <td>Registros</td>
                        <td>Número total de ocurrencias que se encontraron en la columna.</td>
                      </tr>
                      <tr>
                        <td>Valor Máximo</td>
                        <td>Valor máximo encontrado en la columna.</td>
                      </tr>
                      <tr>
                        <td>Valor Mínimo</td>
                        <td>Valor mínimo encontrado en la columna.</td>
                      </tr>
                      <tr>
                        <td>Media</td>
                        <td>Promedio de los valores de la columna.</td>
                      </tr>
                      <tr>
                        <td>Desviación Estándar</td>
                        <td>Dispersión de los datos de la columna con respecto a la media.</td>
                      </tr>
                      <tr>
                        <td>Primer Cuartil</td>
                        <td>Valor que representa el 25% de los datos de la columna.</td>
                      </tr>
                      <tr>
                        <td>Segundo Cuartil</td>
                        <td>Valor que representa el 50% de los datos de la columna</td>
                      </tr>
                      <tr>
                        <td>Tercer Cuartil</td>
                        <td>Valor que representa el 75% de los datos de la columna.</td>
                      </tr>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </Fade>
        </Modal>

        <div className="top">
          <h1 className="title">Resumen de Datos</h1>
          <div className="tableButtons perf">
            <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
          </div>
        </div>
        <div className="table">
          <DataGrid
          rows={dataPerfs}
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