import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { Link } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";

const API = process.env.REACT_APP_API;

export const DataTable = () => {

  const [activeProject, setActiveProject] = useContext(ProjectContext);

  const [projects, setProjects] = useState([]);

  const getProjects = async () =>{
    const res = await fetch(API + '/getProjects/' + localStorage.getItem('email'));
    const data = await res.json();
    setProjects(data);
  }

  useEffect(() => {
    getProjects();
  }, [])

  const activateProject = async (id, name) => {
    await setActiveProject(name);
    localStorage.setItem('project', name);
    localStorage.setItem('projectObjID', id);

    await fetch(API + '/project/' + localStorage.getItem('project'),{
      method: 'POST',
      headers:{
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json"
      },
      body: JSON.stringify(name),
  });

  }

  const deactivateProject = async () =>{
    await setActiveProject('None');
    localStorage.setItem('project', 'None');
    localStorage.removeItem('projectObjID');
  }

  const columns = [
    { field: '_id', hide: true},
    { field: 'id', headerName: "ID" },
    { field: 'ProjectName', headerName: "Nombre de Proyecto", width: 330},
    { field: "DataBaseName", headerName: "Base de Datos", width: 230 },
    { field: "DateCreated", headerName: "Fecha de Creación", width: 330 },
    { field: "action", headerName: "Acción", width: 200, renderCell:(params)=>{
      return(
        <div className="cellAction">
          <div className="viewButton" onClick={() => activateProject(params.row._id, params.row.ProjectName)}>Activar</div>
          <div className="deleteButton" onClick={deactivateProject}>Desactivar</div>
        </div>
      )
    }}
  ];

  return(
      <div className="datatable">
        <div className="manageTable">
          <h1 className="title">Mis Proyectos</h1>
          <Link to="/nuevo"><div className="addButton">Agregar Datos</div></Link>
        </div>
          <DataGrid
          rows={projects}
          columns={columns}
          pageSize={9}
          rowsPerPageOptions={[9]}
          getRowId={(row) => row._id}
          disableSelectionOnClick
          />
      </div>
  )
}