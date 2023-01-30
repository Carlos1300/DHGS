import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { useNavigate } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import LinearProgress from '@mui/material/LinearProgress';
import Swal from "sweetalert2";

const API = process.env.REACT_APP_API;

export const DataSummaryTable = () => {

  const [dataSummary, setDataSummary] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const navigate = useNavigate();

  const getSummary = async () =>{
    const res = await fetch(API + '/summary/' + localStorage.getItem('project'));
    const data = await res.json();
    setDataSummary(data);
    setLoadingTable('disabled');
  }

  useEffect(() => {
    
    if(activeProject !== 'None'){

      getSummary();

    } else {
      Swal.fire({
        title: 'Error al cargar perfilado',
        text: 'Por favor seleccione un proyecto primero.',
        icon: 'error',
        button: 'Seleccionar proyecto',
        confirmButtonColor: "#000"
    });
      navigate('/repo')
    }
    
  }, [navigate, activeProject])

  const columns = [
    { field: 'id', hide: true},
    { field: 'Column', headerName: "Columna", width: 210},
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
          <div className="top">
            <h1 className="title">Sumario de Datos</h1>
          </div>
          <DataGrid
          rows={dataSummary}
          columns={columns}
          pageSize={9}
          rowsPerPageOptions={[9]}
          disableSelectionOnClick
          components={{
            LoadingOverlay: LinearProgress,
          }}
          loading={loadingTable === 'enabled' ? true : false}
          />
      </div>
  )
}