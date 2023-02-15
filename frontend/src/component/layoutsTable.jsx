import React, { useState, useEffect } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { Link } from "react-router-dom";
import LinearProgress from '@mui/material/LinearProgress';
import Swal from 'sweetalert2'
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

const API = process.env.REACT_APP_API;

export const LayoutsTable = () => {

  const [layouts, setLayouts] = useState([]);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

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

  const NoRows = () =>{
    return(
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%"}}>
        <img style={{width: "120", height: "100"}} src="https://static.vecteezy.com/system/resources/thumbnails/010/856/652/small/no-result-data-document-or-file-not-found-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-etc-vector.jpg" alt="No data" />
        <p>No se encontraron layouts.</p>
      </div>
    )
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

        <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
          <Fade in={open}>
            <div className="modalBox">
              <div className="closeBtn" onClick={handleClose}>&times;</div>
              <div className="modalContent">
                <div className="modalTitle">
                    <h3><b>Página de Mis Layouts</b></h3>
                </div>
                <div className="modalText">
                  <p>En esta página podrás encontrar todos los layouts que has agregado al proyecto activo, también tendrás la opción de copiar su nombre al portapapeles para después pegarlo en alguna regla que lo requiera, para esto simplemente da click en la opción <i>Copiar</i>.</p>
                </div>
              </div>
            </div>
          </Fade>
        </Modal>

        <div className="top">
          <h1 className="title">Mis Layouts</h1>
          <div className="tableButtons">
            <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
            <Link to='new'><button className="addButton">Agregar Layout</button></Link>
          </div>
        </div>
        <div className="table">
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
            NoRowsOverlay: NoRows
          }}
          loading={loadingTable === 'enabled' ? true : false}
          />
        </div>
      </div>
  )
}