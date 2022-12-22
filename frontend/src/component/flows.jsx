import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { Link } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import swal from 'sweetalert';

const API = process.env.REACT_APP_API;

export const Flows = () => {

  const [activeProject, setActiveProject] = useContext(ProjectContext)

  const [flows, setFlows] = useState([]);

  const getFlows = async () =>{
    const res = await fetch(API + '/getGeneralFlows/' + localStorage.getItem('email'));
    const data = await res.json();
    setFlows(data);
  }

  useEffect(() => {
    getFlows();
  }, [])

  const importFlow = async (id) => {

    const res = await fetch(API + '/importFlow/' + localStorage.getItem('email') + '/' + localStorage.getItem('project'),{
      method: 'POST',
      headers:{
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json"
      },
      body: JSON.stringify(id),
    });

    const data = await res.json();

    if(res.status !== 200 && data.msg !== ''){
        swal({
            title: 'Error al importar el flujo',
            text: 'Este flujo ya se encuentra en el proyecto.',
            icon: 'error',
            button: 'Volver',
            confirmButtonColor: "#000",
            timer: "10000"
        });

    }else{
        swal({
            title: 'Flujo agregado',
            text: data.msg,
            icon: 'success',
            button: 'Continuar',
            confirmButtonColor: "#000",
            timer: "10000"
        })
    }
  }

  const columns = [
    { field: '_id', hide: true},
    { field: 'id', headerName: "ID" },
    { field: 'FlowName', headerName: "Nombre del flujo", width: 330},    
    { field: "Operations", headerName: "Operaciones", width: 330, renderCell:(params) => {
      return(
        <ul className="flowNames">
          {
            params.row.Sequence.map((item, index) =>(
              <li key={index}>{index + 1 + "." + " " + item.dispname}</li>
            ))
          }
        </ul>
      )
    }},
    { field: "DateCreated", headerName: "Fecha de Creación", width: 300 },
  ];

  const actionColumn = { field: "action", headerName: "Acción", width: 120, renderCell:(params)=>{
    return(
      <div className="cellAction">
        <div className="viewButton" onClick={() => importFlow(params.row._id)}>Importar</div>
      </div>
    )
  }}

  return(
      <div className="datatable">
        <div className="manageTable">
          <h1 className="title">Mis Flujos Generales</h1>
          <Link to="/nuevoflujo"><div className="addButton">Agregar Flujo</div></Link>
        </div>
          <DataGrid
          rows={flows}
          columns={activeProject !== 'None' ? columns.concat(actionColumn) : columns }
          pageSize={9}
          rowsPerPageOptions={[9]}
          getRowId={(row) => row._id}
          getRowHeight={() => 'auto'}
          getEstimatedRowHeight={() => 200}
          disableSelectionOnClick
          />
      </div>
  )
}