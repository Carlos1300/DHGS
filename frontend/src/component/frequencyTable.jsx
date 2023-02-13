import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { ProjectContext } from "../context/projectContext";
import LinearProgress from '@mui/material/LinearProgress';
import Swal from "sweetalert2";

const API = process.env.REACT_APP_API;

export const FrequencyTable = () => {

  const [frequency, setFrequency] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('disabled');
  const [availableFreq, setAvailableFreq] = useState([])

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
        <div className="manageTable">
          <h1 className="title">Frecuencia de Valores</h1>
          <div className="selectColumns">
            <label>Seleccionar columna: </label>
            <select onChange={getColumnFrequency}>
              <option selected disabled value="">Columnas</option>
              {
                availableFreq.map((item, index) => (
                  <option key={index} value={item}>{item}</option>
                ))
              }
            </select>
          </div>
        </div>
          <DataGrid
          rows={frequency}
          columns={columns}
          pageSize={100}
          rowsPerPageOptions={[100]}
          getRowId={(row) => row.ID}
          disableSelectionOnClick
          components={{
            LoadingOverlay: LinearProgress,
          }}
          loading={loadingTable === 'enabled' ? true : false}
          />
      </div>
  )
}