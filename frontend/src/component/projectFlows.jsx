import React, { useState, useEffect } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { Link } from "react-router-dom";
import Swal from 'sweetalert2'
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import LinearProgress from '@mui/material/LinearProgress';


const API = process.env.REACT_APP_API;

export const ProjectFlows = () => {

  const [flows, setFlows] = useState([]);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);


  const getFlows = async () =>{
    const res = await fetch(API + '/project_flows/' + localStorage.getItem('project'));
    const data = await res.json();
    setFlows(data);
    setLoadingTable('disabled');
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

    if(res.status !== 200){
        Swal.fire({
            title: 'Error al aplicar el flujo',
            text: 'Por favor, revise de nuevo los parámetros de su flujo.',
            icon: 'error',
            showConfirmButton: false,
            timer: "10000"
        });

    }else{
        Swal.fire({
            title: 'Aplicación exitosa',
            text: 'Su flujo ha sido aplicado con éxito.',
            icon: 'success',
            showConfirmButton: false,
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

  const NoRows = () =>{
    return(
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%"}}>
        <img style={{width: "120", height: "100"}} src="https://static.vecteezy.com/system/resources/thumbnails/010/856/652/small/no-result-data-document-or-file-not-found-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-etc-vector.jpg" alt="No data" />
        <p>No se encontraron flujos en este proyecto.</p>
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
        
        <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
          <Fade in={open}>
            <div className="modalBox">
              <div className="closeBtn" onClick={handleClose}>&times;</div>
              <div className="modalContent">
                <div className="modalTitle">
                    <h3><b>Página de Flujos del Proyecto</b></h3>
                </div>
                <div className="modalText">
                  <p>En esta página podrás encontrar todos los flujos que han sido importados al proyecto activo, también tendrás la posibilidad de aplicarlos, para esto simplemente da click en la opción <i>Aplicar</i> para comenzar con el proceso.</p>
                </div>
              </div>
            </div>
          </Fade>
        </Modal>

        <div className="top">
          <h1 className="title">Flujos del Proyecto: {localStorage.getItem('project')}</h1>
          <div className="tableButtons">
            <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
            <Link to='/nuevoflujo'><button className="addButton">Agregar Flujo</button></Link>
          </div>
        </div>
        <div className="table">
          <DataGrid
          rows={flows}
          columns={columns}
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