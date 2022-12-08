import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import DriveFolderUploadIcon from '@mui/icons-material/DriveFolderUpload';

const API = process.env.REACT_APP_API;

export const New = () =>{

    const [file, setFile] = useState("");

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Agregar Datos</h1>
                </div>
                <div className="bottom">
                    <div className="left">
                        <img src={file ? "https://static.thenounproject.com/png/3163111-200.png" : "https://static.thenounproject.com/png/140281-200.png"} alt="" className="placeholderImg" />
                    </div>
                    <div className="right">
                        <form action={API + '/addProject/' + localStorage.getItem('email')} method="POST" encType="multipart/form-data">
                            <div className="formInput">
                                <label htmlFor="file">Fuente de Datos: <DriveFolderUploadIcon className="icon" /></label>
                                <input type="file" id="file" name="dataFile" onChange={e=>setFile(e.target.files[0])} style={{display: "none"}} accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"/>
                            </div>
                            <div className="formInput">
                                <label>Nombre de Proyecto</label>
                                <input type="text" placeholder="Indique le nombre del proyecto" />
                            </div>
                            <div className="formInput">
                                <label>Tipo de Archivo</label>
                                <select name="fileType">
                                    <option value="csv" selected>CSV</option>
                                    <option value="xlsx">XLSX</option>
                                    <option value="txt">TXT</option>
                                    <option value="json">JSON</option>
                                </select>
                            </div>
                            <div className="formInput">
                                <label>Separador</label>
                                <input type="text" name="sep" placeholder="Indique el separador" />
                            </div>
                            <div className="formInput">
                                <label>Codificación</label>
                                <select name="enc">
                                    <option value="UTF-8" selected>UTF-8</option>
                                    <option value="ISO">ISO</option>
                                    <option value="LATIN">LATIN</option>
                                    <option value="OTRO">OTRO</option>
                                </select>
                            </div>
                            <div className="formInput"></div>
                            <button className="sendButton">Send</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    )
}