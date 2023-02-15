import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { Link } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import Swal from 'sweetalert2';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import LinearProgress from '@mui/material/LinearProgress';

const API = process.env.REACT_APP_API;

export const Flows = () => {

  const [activeProject] = useContext(ProjectContext)

  const [flows, setFlows] = useState([]);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const getFlows = async () =>{
    const res = await fetch(API + '/my_flows/' + localStorage.getItem('email'));
    const data = await res.json();
    setFlows(data);
    setLoadingTable('disabled');
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
        Swal.fire({
            title: 'Error al importar el flujo',
            text: 'Este flujo ya se encuentra en el proyecto.',
            icon: 'error',
            button: 'Volver',
            confirmButtonColor: "#000",
            timer: "10000"
        });

    }else{
        Swal.fire({
            title: 'Flujo agregado',
            text: data.msg,
            icon: 'success',
            button: 'Continuar',
            confirmButtonColor: "#000",
            timer: "10000"
        })
    }
  }

  const deleteFlow = async (objId, id) => {

    const res = await fetch(API + '/my_flows/' + localStorage.getItem('email'),{
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
            title: 'Error al importar el flujo',
            text: 'Este flujo ya se encuentra en el proyecto.',
            icon: 'error',
            button: 'Volver',
            confirmButtonColor: "#000",
            timer: "10000"
        });
    }else{

      Swal.fire({
          title: 'Flujo eliminado',
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

  const NoRows = () =>{
    return(
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%"}}>
        <img style={{width: "120", height: "100"}} src="https://static.vecteezy.com/system/resources/thumbnails/010/856/652/small/no-result-data-document-or-file-not-found-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-etc-vector.jpg" alt="No data" />
        <p>No se encontraron flujos.</p>
      </div>
    )
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
  ];

  const actionColumn = { field: "action", headerName: "Acción", width: 170, renderCell:(params)=>{
    return(
      <div className="cellAction">
        <div className="viewButton" onClick={() => importFlow(params.row._id)}>Importar</div>
        <div className="deleteButton" onClick={() => deleteFlow(params.row._id, params.row.id)}>Eliminar</div>
      </div>
    )
  }}

  return(
      <div className="datatable">
        <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
          <Fade in={open}>
            <div className="modalBox">
              <div className="closeBtn" onClick={handleClose}>&times;</div>
              <div className="modalContent">
                <div className="modalTitle">
                    <h3><b>Página de Flujos Generales</b></h3>
                </div>
                <div className="modalText">
                  <p>En esta página podrás encontrar todos los flujos que han sido creados y agregados con éxito al DataHub, también tendrás la posibilidad de importarlos al proyecto que tengas activo en ese momento, para esto simplemente da click en la opción <i>Importar</i> para agregar el flujo a los flujos del proyecto y así poder aplicarlos.</p>
                </div>
              </div>
            </div>
          </Fade>
        </Modal>

        <div className="top">
          <h1 className="title">Mis Flujos Generales</h1>
          <div className="tableButtons">
            <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
            <Link to='/nuevoflujo'><button className="addButton">Agregar Flujo</button></Link>
          </div>
        </div>
        <div className="table">
          <DataGrid
          rows={flows}
          columns={activeProject !== 'None' ? columns.concat(actionColumn) : columns }
          pageSize={9}
          rowsPerPageOptions={[9]}
          getRowId={(row) => row._id}
          getRowHeight={() => 'auto'}
          getEstimatedRowHeight={() => 200}
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