import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { Link } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";

const columns = [
  { field: '_id', hide: true},
  { field: 'id', headerName: "ID" },
  { field: 'ProjectName', headerName: "Nombre de Proyecto", width: 330},
  { field: "DataBaseName", headerName: "Base de Datos", width: 230 },
  { field: "DateCreated", headerName: "Fecha y Hora de Creación", width: 330 }
  // { field: "status", headerName: "Estado", width: 160,
  // renderCell: (params) =>{
  //   return(
  //     <div className={`cellWithStatus ${params.row.status}`}>{params.row.status}</div>
  //   )
  // }}
  // { field: 'lastName', headerName: 'Last name', width: 130 },
  // {
  //   field: 'age',
  //   headerName: 'Age',
  //   type: 'number',
  //   width: 90,
  // },
  // {
  //   field: 'fullName',
  //   headerName: 'Full name',
  //   description: 'This column has a value getter and is not sortable.',
  //   sortable: false,
  //   width: 160,
  //   // renderCell: (params) =>{
  //   //     return(HTML)
  //   // } Para renderear algún elemento HTML
  //   valueGetter: (params) =>
  //     `${params.row.firstName || ''} ${params.row.lastName || ''}`,
  // },
];

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
    localStorage.setItem('project', name)
  }

  const deactivateProject = async () =>{
    await setActiveProject('None');
    localStorage.setItem('project', 'None')
  }

  const actionColumn = [
    { field: "action", headerName: "Acción", width: 200, renderCell:(params)=>{
      return(
        <div className="cellAction">
          <div className="viewButton" onClick={() => activateProject(params.row._id, params.row.ProjectName)}>Activar</div>
          <div className="deleteButton" onClick={deactivateProject}>Desactivar</div>
        </div>
      )
    }}
  ]

  return(
      <div className="datatable">
        <div className="manageTable">
          <Link to="/nuevo"><div className="addButton">Agregar Datos</div></Link>
        </div>
          <DataGrid
          rows={projects}
          columns={columns.concat(actionColumn)}
          pageSize={9}
          rowsPerPageOptions={[9]}
          getRowId={(row) => row._id}
          disableSelectionOnClick
          />
      </div>
  )
}