import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { useNavigate } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import swal from "sweetalert";

const API = process.env.REACT_APP_API;

export const DataLoadsTable = () => {

  const [dataLoads, setDataLoads] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const navigate = useNavigate();

  const getPerfs = async () =>{
    const res = await fetch(API + '/getDataLoads/' + localStorage.getItem('email') + '/' + localStorage.getItem('project'));
    const data = await res.json();
    setDataLoads(data);
  }

  useEffect(() => {
    
    if(activeProject !== 'None'){

      getPerfs();

    } else {
      swal({
        title: 'Error al cargar el historial de cargas',
        text: 'Por favor seleccione un proyecto primero.',
        icon: 'error',
        button: 'Seleccionar proyecto',
        confirmButtonColor: "#000"
    });
      navigate('/repo')
    }
    
  }, [navigate, activeProject])

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
          <div className="top">
            <h1 className="title">Cargas de Datos</h1>
          </div>
          <DataGrid
          rows={dataLoads}
          columns={columns}
          pageSize={9}
          rowsPerPageOptions={[9]}
          disableSelectionOnClick
          />
      </div>
  )
}