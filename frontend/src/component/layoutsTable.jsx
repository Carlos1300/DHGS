import React, { useState, useEffect } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { Link } from "react-router-dom";
import LinearProgress from '@mui/material/LinearProgress';
import Swal from 'sweetalert2'

const API = process.env.REACT_APP_API;

export const LayoutsTable = () => {

  const [layouts, setLayouts] = useState([]);
  const [loadingTable, setLoadingTable] = useState('enabled');

  const getLayouts = async () =>{
    const res = await fetch(API + '/layouts/' + localStorage.getItem('project'));
    const data = await res.json();
    setLayouts(data);
    setLoadingTable('disabled')
  }

  useEffect(() => {
    getLayouts();
  }, [])

  const copyName = async () =>{
    const Toast = Swal.mixin({
      toast: true,
      position: 'bottom-end',
      showConfirmButton: false,
      timer: 1500,
      didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer)
        toast.addEventListener('mouseleave', Swal.resumeTimer)
      }
    })
    
    Toast.fire({
      title: 'Nombre copiado al portapapeles',
      background: 'limegreen',
      color: '#FFF'
    })
  }

  const deleteRule = async (id, objId) => {

    const res = await fetch(API + '/layouts/' + localStorage.getItem('project'),{
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
        const Toast = Swal.mixin({
        toast: true,
        position: 'bottom-end',
        showConfirmButton: false,
        timer: 1500,
        didOpen: (toast) => {
          toast.addEventListener('mouseenter', Swal.stopTimer)
          toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
      })
    
      Toast.fire({
        title: data.msg,
        background: 'limegreen',
        color: '#FFF'
      })

      setLayouts((prevLayouts) =>
      prevLayouts.filter((_, index) => index !== id)
      );
    }
  }

  const columns = [
    { field: '_id', hide: true},
    { field: 'id', headerName: 'ID', width: 50},
    { field: 'name', headerName: "Nombre de la Regla", width: 300},
    { field: 'description', headerName: "Descripción", width: 700},
    { filed: "action", headerName: "Acciones", width: 160, renderCell:(params)=>{
      return(
        <div className="cellAction" key={params.row._id}>
          <CopyToClipboard text={params.row.name}><div className="copyButton" onClick={copyName}>Copiar</div></CopyToClipboard>
          <div className="deleteButton" onClick={() => deleteRule(params.row.id, params.row._id)}>Eliminar</div>
            
        </div>
      )
    }}
  ];

  return(
      <div className="datatable">
        <div className="manageTable">
          <h1 className="title">Layouts</h1>
          <Link to="new"><div className="addButton">Agregar Layout</div></Link>
        </div>
          <DataGrid
          rows={layouts}
          columns={columns}
          getRowId={(row) => row._id}
          pageSize={9}
          rowsPerPageOptions={[9]}
          getEstimatedRowHeight={() => 400}
          disableSelectionOnClick
          components={{
            LoadingOverlay: LinearProgress,
          }}
          loading={loadingTable === 'enabled' ? true : false}
          />
      </div>
  )
}