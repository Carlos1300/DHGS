import React, { useState, useEffect } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { Link } from "react-router-dom";
// import { ProjectContext } from "../context/projectContext";
import Swal from 'sweetalert2'

const API = process.env.REACT_APP_API;

export const ProjectFlows = () => {

  const [flows, setFlows] = useState([]);

  const getFlows = async () =>{
    const res = await fetch(API + '/project_flows/' + localStorage.getItem('project'));
    const data = await res.json();
    setFlows(data);
  }

  useEffect(() => {
    getFlows();
  }, [])

  const applyFlow = async (id) => {
    Swal.fire({
      title: 'Aplicando flujo.',
      html: 'Su flujo está siendo aplicado, por favor espere.<br><br><b><style="color: crimson;">No cierre esta ventana hasta el que proceso haya terminado.</style></b>',
      imageUrl: 'https://www.tuyu.mx/assets/loader.gif',
      imageWidth: 100,
      imageHeight: 100,
      imageAlt: 'Custom image',
      confirmButtonColor: "#000",
      showConfirmButton: false,
      allowOutsideClick: false
    });

    const res = await fetch(API + '/applyFlow/' + localStorage.getItem('project'),{
      method: 'POST',
      headers:{
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json"
      },
      body: JSON.stringify(id),
    });

    const data = await res.json();

    if(res.status !== 200 && data.msg !== ''){
        Swal.fire({
            title: 'Error al cargar la fuente de datos',
            text: 'Revise de nuevo los campos.',
            icon: 'error',
            button: 'Volver a intentarlo',
            confirmButtonColor: "#000",
            timer: "10000"
        });

    }else{
        Swal.fire({
            title: 'Aplicación exitosa',
            text: data.msg,
            icon: 'success',
            button: 'Continuar',
            confirmButtonColor: "#000",
            timer: "10000"
      })
    }
  }

  const deleteFlow = async (objId, id) => {

    const res = await fetch(API + '/project_flows/' + localStorage.getItem('project'),{
      method: 'DELETE',
      headers:{
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json"
      },
      body: JSON.stringify(objId),
    });

    const data = await res.json();

    if(res.status !== 200 && data.msg !== ''){
        Swal.fire({
            title: 'Error al eliminar el flujo',
            text: 'Revise de nuevo los campos.',
            icon: 'error',
            button: 'Volver a intentarlo',
            confirmButtonColor: "#000",
            timer: "10000"
        });

    }else{
        Swal.fire({
            title: 'Se eliminó el flujo',
            text: data.msg,
            icon: 'success',
            button: 'Continuar',
            confirmButtonColor: "#000",
            timer: "10000"
      })

      setFlows((flows) => {
        const rowToDeleteIndex = id - 1;
        return [
          ...flows.slice(0, rowToDeleteIndex),
          ...flows.slice(rowToDeleteIndex + 1),
        ];
      });
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
              <li key={index}>{(index + 1) + ". " + item.dispname}</li>
            ))
          }
        </ul>
      )
    }},
    { field: "DateCreated", headerName: "Fecha de Creación", width: 150 },
    { field: "action", headerName: "Acción", width: 170, renderCell:(params)=>{
      return(
        <div className="cellAction">
          <div className="viewButton" onClick={() => applyFlow(params.row._id)}>Aplicar</div>
          <div className="deleteButton" onClick={() => deleteFlow(params.row._id, params.row.id)}>Eliminar</div>
        </div>
      )
    }}
  ];

  return(
      <div className="datatable">
        <div className="manageTable">
          <h1 className="title">Flujos del Proyecto: {localStorage.getItem('project')}</h1>
          <Link to="/nuevoflujo"><div className="addButton">Agregar Flujo</div></Link>
        </div>
          <DataGrid
          rows={flows}
          columns={columns}
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