import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { Link } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import LinearProgress from '@mui/material/LinearProgress';
import Swal from 'sweetalert2';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';


const API = process.env.REACT_APP_API;

export const DataTable = () => {

  const [activeProject, setActiveProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const [projects, setProjects] = useState([]);
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const getProjects = async () =>{
    const res = await fetch(API + '/getProjects/' + localStorage.getItem('email'));
    const data = await res.json();
    setProjects(data);
    setLoadingTable('disabled');
  }

  useEffect(() => {
    getProjects();
  }, [])

  const activateProject = async (id, name) => {
    await setActiveProject(name);
    localStorage.setItem('project', name);
    localStorage.setItem('projectObjID', id);

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
      title: 'Proyecto activado: ' + name,
      background: 'limegreen',
      color: '#FFF'
    })
  }

  const deactivateProject = async () =>{
    await setActiveProject('None');
    localStorage.setItem('project', 'None');
    localStorage.removeItem('projectObjID');

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
      title: 'Proyecto desactivado',
      background: 'crimson',
      color: '#FFF'
    })
  }

  const NoRows = () =>{
    return(
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%"}}>
        <img style={{width: "120", height: "100"}} src="https://static.vecteezy.com/system/resources/thumbnails/010/856/652/small/no-result-data-document-or-file-not-found-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-etc-vector.jpg" alt="No data" />
        <p>No se encontraron proyectos.</p>
      </div>
    )
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
      <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
        <Fade in={open}>
          <div className="modalBox">
            <div className="closeBtn" onClick={handleClose}>&times;</div>
            <div className="modalContent">
              <div className="modalTitle">
                  <h3><b>Página de Mis Proyectos</b></h3>
              </div>
              <div className="modalText">
                <p>En esta página podrás encontrar todos los proyectos que has agregado al DataHub, también tendrás la opción de seleccionar en cuál de ellos deseas trabajar, para esto simplemente da click en la opción <i>Activar</i>.</p>
              </div>
            </div>
          </div>
        </Fade>
      </Modal>

      <div className="top">
        <h1 className="title">Mis Proyectos</h1>
        <div className="tableButtons">
          <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
          <Link to='/nuevo'><button className="addButton">Agregar Datos</button></Link>
        </div>
      </div>
      <div className="table">
        <DataGrid
        rows={projects}
        columns={columns}
        pageSize={9}
        rowsPerPageOptions={[9]}
        getRowId={(row) => row._id}
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