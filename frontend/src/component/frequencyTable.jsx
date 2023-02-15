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

export const FrequencyTable = () => {

  const [frequency, setFrequency] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('disabled');
  const [availableFreq, setAvailableFreq] = useState([])
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const getColumnFrequency = async (e) => {

    let selectedColumn = e.target.value;

    setLoadingTable('enabled');
    const res = await fetch(API + '/frequency/' + localStorage.getItem('project'),{
      method: 'POST',
      headers:{
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json"
      },
      body: JSON.stringify(selectedColumn),
    });
    const data = await res.json();
    setFrequency(data);
    setLoadingTable('disabled');
  }

  const getFreqs = async() => {
    const freqs = await fetch(API + '/frequency/' + localStorage.getItem('project'));
    const data = await freqs.json();
    setAvailableFreq(data);
  }

  useEffect(() => {
    getFreqs();
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
    { field: "ID", hide: true},
    { field: "Phrase", headerName: "Frase", width: 190},
    { field: "id", headerName: "Identificador", width: 450 },
    { field: "Words", headerName: "Palabras", width: 130 },
    { field: "Frequency", headerName: "Frecuencia", width: 130 },
    { field: "Distribution", headerName: "Distribución %", width: 160 },
    { field: "Category", headerName: "Categoría", width: 150 }
    ];

  return(
    <div className="datatable">
      <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
        <Fade in={open}>
          <div className="modalBox">
            <div className="closeBtn" onClick={handleClose}>&times;</div>
            <div className="modalContent">
              <div className="modalTitle">
                  <h3><b>Página de Frecuencia de Valores</b></h3>
              </div>
              <div className="modalText">
                <p>En esta página podrás encontrar el estudio de las frecuencias de valores de una columna generado por la regla <b><i>Obtener frecuencia de valores</i></b> al ser ejecutada por algún flujo. Para obtener el estudio generado es necesario seleccionar la columna que fue seleccionada en el flujo para aplicar la regla, para esto busca y selecciona dicha columna en el menú <i>Seleccionar Columna</i>.</p>
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
                        <td>Frase</td>
                        <td>Porción de texto de una palabra de la columna.</td>
                      </tr>
                      <tr>
                        <td>Identificador</td>
                        <td>Palabra a la que pertenece la frase extraída.</td>
                      </tr>
                      <tr>
                        <td>Palabras</td>
                        <td>Cantidad de palabras de las que consta la frase.</td>
                      </tr>
                      <tr>
                        <td>Frecuencia</td>
                        <td>Número de veces que fue encontrada la frase en la columna.</td>
                      </tr>
                      <tr>
                        <td>Distribución</td>
                        <td>Porcentaje de aparición de la frase en la columna.</td>
                      </tr>
                      <tr>
                        <td>Categoría</td>
                        <td>Tipo al que pertenece la frase en cuestión.</td>
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
        <h1 className="title">Frecuencia de Valores</h1>
        <div className="tableButtons freq">
          <button className="helpButton" onClick={handleOpen}><QuestionMarkIcon /></button>
          <div className="selectColumns">
            <select onChange={getColumnFrequency}>
              <option selected disabled value="">Seleccionar Columna</option>
              {
                availableFreq.map((item, index) => (
                  <option key={index} value={item}>{item}</option>
                ))
              }
            </select>
          </div>

        </div>
      </div>
      <div className="table">
          <DataGrid
          rows={frequency}
          columns={columns}
          pageSize={100}
          rowsPerPageOptions={[100]}
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