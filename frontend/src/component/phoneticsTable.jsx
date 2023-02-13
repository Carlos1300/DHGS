import React, { useState, useEffect, useContext } from "react";
import "../general.scss";
import { DataGrid } from '@mui/x-data-grid';
import { useNavigate } from "react-router-dom";
import { ProjectContext } from "../context/projectContext";
import LinearProgress from '@mui/material/LinearProgress';
import Swal from "sweetalert2";

const API = process.env.REACT_APP_API;

export const PhoneticsTable = () => {

  const [phonetics, setPhonetics] = useState([]);
  const [activeProject] = useContext(ProjectContext);
  const [loadingTable, setLoadingTable] = useState('disabled');
  const [availablePhon, setAvailablePhon] = useState([])
  const navigate = useNavigate();

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

  console.log(availablePhon)

  useEffect(() => {
    getPhons();
  }, [])

  const columns = [
    { field: 'ID', hide: true},
    { field: 'Word', headerName: "Palabra", width: 395},
    { field: "Soundex", headerName: "Soundex", width: 130 },
    { field: "Freq Soundex", headerName: "Frec. Soundex", width: 130 },
    { field: "Dist Soundex", headerName: "Dist. Soundex", width: 130 },
    { field: "Metaphone", headerName: "Metáfono", width: 160 },
    { field: "Freq Metaphone", headerName: "Frec. Metáfono", width: 150 },
    { field: "Dist Metaphone", headerName: "Dist. Metáfono", width: 130 }
  ];

  return(
      <div className="datatable">
        <div className="manageTable">
          <h1 className="title">Fonéticos</h1>
          <div className="selectColumns">
            <label>Seleccionar columna: </label>
            <select onChange={getColumnPhonetics}>
              <option selected disabled value="">Columnas</option>
              {
                availablePhon.map((item, index) => (
                  <option key={index} value={item}>{item}</option>
                ))
              }
            </select>
          </div>
        </div>
          <DataGrid
          rows={phonetics}
          columns={columns}
          pageSize={9}
          rowsPerPageOptions={[9]}
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