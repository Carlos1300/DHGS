import React, { useState, useEffect } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { Link } from "react-router-dom";
import LinearProgress from '@mui/material/LinearProgress';
import Swal from 'sweetalert2';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

const API = process.env.REACT_APP_API;

export const CatalogsTable = () => {

  const [catalogs, setCatalogs] = useState([]);
  const [loadingTable, setLoadingTable] = useState('enabled');
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const getCatalogs = async () =>{
    const res = await fetch(API + '/catalogs/' + localStorage.getItem('email'));
    const data = await res.json();

    if(data.msg !== '' && res.status !== 200){
      Swal.fire({
        title: 'Error al cargar catálogos',
        text: data.msg,
        icon: 'error',
        button: 'Volver a intentarlo',
        confirmButtonColor: "#000",
        timer: "10000"
      });
      setCatalogs(data);
      setLoadingTable('disabled');
    }else{
      setCatalogs(data);
      setLoadingTable('disabled');
    }
  }

  useEffect(() => {
    getCatalogs();
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

  const deleteCatalog = async (id, objId) => {

    const res = await fetch(API + '/catalogs/' + localStorage.getItem('email'),{
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

      id = id - 1

      setCatalogs((prevCatalogs) =>
      prevCatalogs.filter((_, index) => index !== id)
      );
    }
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
    { field: 'id', headerName: 'ID', width: 50},
    { field: 'name', headerName: "Nombre del Catálogo", width: 250},
    { field: 'description', headerName: "Descripción", width: 750},
    { filed: "action", headerName: "Acciones", width: 160, renderCell:(params)=>{
      return(
        <div className="cellAction" key={params.row._id}>
          <CopyToClipboard text={params.row.name}><div className="copyButton" onClick={copyName}>Copiar</div></CopyToClipboard>
          {
            params.row.user === 'Public' ? (
              <></>
            ) : (
              <div className="deleteButton" onClick={() => deleteCatalog(params.row.id, params.row._id)}>Eliminar</div>
            )
          }
            
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
                    <h3><b>Página de Mis Catálogos</b></h3>
                </div>
                <div className="modalText">
                  <p>En esta página podrás encontrar todos los catálogos que has agregado al DataHub, también tendrás la opción de copiar su nombre al portapapeles para después pegarlo en alguna regla que lo requiera, para esto simplemente da click en la opción <i>Copiar</i>.</p>
                </div>
              </div>
            </div>
          </Fade>
        </Modal>

        <div className="top">
          <h1 className="title">Mis Catálogos</h1>
          <div className="tableButtons">
            <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
            <Link to='new'><button className="addButton">Agregar Catálogo</button></Link>
          </div>
        </div>
        <div className="table">
          <DataGrid
          rows={catalogs}
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