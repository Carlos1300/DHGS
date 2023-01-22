import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { useNavigate } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import Swal from "sweetalert2";

const API = process.env.REACT_APP_API;

export const DataPerfTable = () => {

  const [dataPerfs, setDataPerfs] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const navigate = useNavigate();

  const getPerfs = async () =>{
    const res = await fetch(API + '/getDataPerf/' + localStorage.getItem('email') + '/' + localStorage.getItem('project'));
    const data = await res.json();
    setDataPerfs(data);
  }

  useEffect(() => {
    
    if(activeProject !== 'None'){

      getPerfs();

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
    { field: 'Column', headerName: "Columna", width: 180},
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
          <div className="top">
            <h1 className="title">Perfilado de Datos</h1>
          </div>
          <DataGrid
          rows={dataPerfs}
          columns={columns}
          pageSize={9}
          rowsPerPageOptions={[9]}
          disableSelectionOnClick
          />
      </div>
  )
}