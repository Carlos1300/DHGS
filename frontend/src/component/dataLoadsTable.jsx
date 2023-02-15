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

export const DataLoadsTable = () => {

  const [dataLoads, setDataLoads] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const getLoads = async () =>{
    const res = await fetch(API + '/getDataLoads/' + localStorage.getItem('email') + '/' + localStorage.getItem('project'));
    if(res.status !== 200){
      setDataLoads([]);
      setLoadingTable('disabled');
    }else{
      const data = await res.json();
      setDataLoads(data);
      setLoadingTable('disabled');
    }
  }

  useEffect(() => {
    getLoads();
  }, [])

  const NoRows = () =>{
    return(
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%"}}>
        <img style={{width: "120", height: "100"}} src="https://static.vecteezy.com/system/resources/thumbnails/010/856/652/small/no-result-data-document-or-file-not-found-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-etc-vector.jpg" alt="No data" />
        <p>No se ha cargado ningún archivo a este proyecto.</p>
      </div>
    )
  }

  const columns = [
    { field: '_id', hide: true},
    { field: 'id', headerName: 'ID', width: 50},
    { field: 'FileName', headerName: "Archivo Fuente", width: 350},
    { field: 'SourceType', headerName: "Tipo de Archivo", width: 150},
    { field: "Encoding", headerName: "Codificación", width: 130 },
    { field: "Rows", headerName: "Número de Registros", width: 180 },
    { field: "Columns", headerName: "Número de Columnas", width: 180 },
    { filed: "Status", headerName: "Estado de Carga", width: 160, renderCell:(params) => {
     return(
      <div className="cellWithStatus memory">{params.row.Status}</div>
     ) 
    }}
  ];

  return(
    <div className="datatable">
      <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
        <Fade in={open}>
          <div className="modalBox">
            <div className="closeBtn" onClick={handleClose}>&times;</div>
            <div className="modalContent">
              <div className="modalTitle">
                  <h3><b>Página de Cargas de Datos</b></h3>
              </div>
              <div className="modalText">
                <p>En esta página podrás consultar el estado de la carga de tu archivo de fuente de datos (previamente añadida al DataHub desde la página de importar) para el proyecto que se encuentra activo.</p>
              </div>
            </div>
          </div>
        </Fade>
      </Modal>

      <div className="top">
        <h1 className="title">Cargas de Datos</h1>
        <div className="tableButtons perf">
          <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
        </div>
      </div>
      <div className="table">
        <DataGrid
        rows={dataLoads}
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