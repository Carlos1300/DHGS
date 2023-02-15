import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { ProjectContext } from "../context/projectContext";
import LinearProgress from '@mui/material/LinearProgress';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

const API = process.env.REACT_APP_API;

export const PhoneticsTable = () => {

  const [phonetics, setPhonetics] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('disabled');
  const [availablePhon, setAvailablePhon] = useState([]);
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const getColumnPhonetics = async (e) => {

    let selectedColumn = e.target.value;

    setLoadingTable('enabled');
    const res = await fetch(API + '/phonetics/' + localStorage.getItem('project'),{
      method: 'POST',
      headers:{
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json"
      },
      body: JSON.stringify(selectedColumn),
    });
    const data = await res.json();
    setPhonetics(data);
    setLoadingTable('disabled');
  }

  const getPhons = async() => {
    const phons = await fetch(API + '/phonetics/' + localStorage.getItem('project'));
    const data = await phons.json();
    setAvailablePhon(data);
  }

  useEffect(() => {
    getPhons();
  }, [])

  const NoRows = () =>{
    return(
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%"}}>
        <img style={{width: "120", height: "100"}} src="https://static.vecteezy.com/system/resources/thumbnails/010/856/652/small/no-result-data-document-or-file-not-found-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-etc-vector.jpg" alt="No data" />
        <p>Por favor seleccione una columna.</p>
      </div>
    )
  }

  const columns = [
    { field: 'ID', hide: true},
    { field: 'Word', headerName: "Palabra", width: 375},
    { field: "Soundex", headerName: "Soundex", width: 130 },
    { field: "Freq Soundex", headerName: "Frec. Soundex", width: 130 },
    { field: "Dist Soundex", headerName: "Dist. Soundex", width: 130 },
    { field: "Metaphone", headerName: "Metáfono", width: 160 },
    { field: "Freq Metaphone", headerName: "Frec. Metáfono", width: 150 },
    { field: "Dist Metaphone", headerName: "Dist. Metáfono", width: 130 }
  ];

  return(
    <div className="datatable">
      <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
        <Fade in={open}>
          <div className="modalBox">
            <div className="closeBtn" onClick={handleClose}>&times;</div>
            <div className="modalContent">
              <div className="modalTitle">
                  <h3><b>Página de Fonéticos</b></h3>
              </div>
              <div className="modalText">
                <p>En esta página podrás encontrar el estudio de los fonéticos de una columna generado por la regla <b><i>Validar fonéticos</i></b> al ser ejecutada por algún flujo. Para obtener el estudio generado es necesario seleccionar la columna que fue seleccionada en el flujo para aplicar la regla, para esto busca y selecciona dicha columna en el menú <i>Seleccionar Columna</i>.</p>
                <p>A continuación, se presenta un desglose de las columnas contenidas y su significado.</p>
                <div className="modalTable">
                  <table>
                    <thead>
                      <tr>
                          <th style={{width: "20%"}}>Columna</th>
                          <th style={{width: "80%"}}>Descripción</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Palabra</td>
                        <td>Palabra encontrada en la columna seleccionada.</td>
                      </tr>
                      <tr>
                        <td>Soundex</td>
                        <td>Soundex de la palabra en cuestión.</td>
                      </tr>
                      <tr>
                        <td>Frec. Soundex</td>
                        <td>Número de apariciones del soundex en la columna seleccionada.</td>
                      </tr>
                      <tr>
                        <td>Dist. Soundex</td>
                        <td>Porcentaje de aparición del soundex en la columna seleccionada</td>
                      </tr>
                      <tr>
                        <td>Metáfono</td>
                        <td>Metáfono de la palabra en cuestión.</td>
                      </tr>
                      <tr>
                        <td>Frec. Metáfono</td>
                        <td>Número de apariciones del metáfono en la columna seleccionada.</td>
                      </tr>
                      <tr>
                        <td>Dist. Metáfono</td>
                        <td>Porcentaje de aparición del metáfono en la columna seleccionada</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </Fade>
      </Modal>

      <div className="top">
        <h1 className="title">Fonéticos</h1>
        <div className="tableButtons freq">
          <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
          <div className="selectColumns">
            <select onChange={getColumnPhonetics}>
              <option selected disabled value="">Seleccionar Columna</option>
              {
                availablePhon.map((item, index) => (
                  <option key={index} value={item}>{item}</option>
                ))
              }
            </select>
          </div>

        </div>
      </div>
      <div className="table">
        <DataGrid
        rows={phonetics}
        columns={columns}
        pageSize={9}
        rowsPerPageOptions={[9]}
        getRowId={(row) => row.ID}
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