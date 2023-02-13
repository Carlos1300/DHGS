import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import DriveFolderUploadIcon from '@mui/icons-material/DriveFolderUpload';
import Swal from 'sweetalert2';

const API = process.env.REACT_APP_API;

export const New = () =>{

    const [file, setFile] = useState("");
    const [projectName, setProjectName] = useState("");
    const [fileType, setFileType] = useState("csv");
    const [sep, setSep] = useState("");
    const [enc, setEnc] = useState("UTF-8");
    const [sheet, setSheet] = useState("");

    const handleSubmit = async (e) => {

        e.preventDefault();

        const form = new FormData();
        form.append('dataSource', file);
        form.append('pName', projectName);
        form.append('fileType', fileType);
        form.append('sep', sep);
        form.append('enc', enc);
        form.append('sheet', sheet);

        const res = await fetch(API + '/addProject/' + localStorage.getItem('email'),{
            method: 'POST',
            headers:{
                "Access-Control-Allow-Origin": "*"
            },
            body: form
        });

        const data = await res.json();

        if(res.status !== 200 && data.msg !== ''){
            Swal.fire({
                title: 'Error al cargar la fuente de datos',
                text: 'Revise de nuevo los campos.',
                icon: 'error',
                button: 'Volver a intentarlo',
                confirmButtonColor: "#000",
                timer: "10000"
            });

            setFile('');
            setProjectName('');
            setFileType('');
            setSep('');
            setEnc('');

        }else{
            Swal.fire({
                title: 'Carga exitosa',
                text: data.msg + ' : ' + data.objID,
                icon: 'success',
                button: 'Continuar',
                confirmButtonColor: "#000",
                timer: "10000"
            })

            setFile('');
            setProjectName('');
            setFileType('');
            setSep('');
            setEnc('');
        }
        
    }

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Importar Datos</h1>
                </div>
                <div className="bottom">
                    <div className="left">
                        <img src={file ? "https://static.thenounproject.com/png/3163111-200.png" : "https://static.thenounproject.com/png/140281-200.png"} alt="" className="placeholderImg" />
                    </div>
                    <div className="right">
                        <form onSubmit={handleSubmit}>
                            <div className="formInput">
                                <label htmlFor="file">Fuente de Datos: <DriveFolderUploadIcon className="icon" /></label>
                                <input type="file" id="file" name="dataSource" onChange={e => setFile(e.target.files[0])} style={{display: "none"}} accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel, .txt"/>
                            </div>
                            <div className="formInput">
                                <label>Nombre de Proyecto</label>
                                <input type="text" name="pName" value={projectName} placeholder="Indique el nombre del proyecto" onChange={e => setProjectName(e.target.value)}/>
                            </div>
                            <div className="formInput">
                                <label>Tipo de Archivo</label>
                                <select name="fileType" onChange={e => setFileType(e.target.value)}>
                                    <option value="csv" selected>CSV</option>
                                    <option value="xlsx">XLSX</option>
                                    <option value="txt">TXT</option>
                                    <option value="json">JSON</option>
                                </select>
                            </div>
                            <div className="formInput">
                                <label>Separador</label>
                                <input type="text" name="sep" value={sep} placeholder="Indique el separador" onChange={e => setSep(e.target.value)}/>
                            </div>
                            <div className="formInput">
                                <label>Codificación</label>
                                <select name="enc" onChange={e => setEnc(e.target.value)}>
                                    <option value="UTF-8" selected>UTF-8</option>
                                    <option value="ISO-8859-1">ISO-8859-1</option>
                                    <option value="LATIN-1">LATIN-1</option>
                                    <option value="OTRO">OTRO</option>
                                </select>
                            </div>
                            {
                                fileType === 'xlsx' ? (

                                    <div className="formInput">
                                        <label>Hoja</label>
                                        <input type="text" name="sheet" value={sheet} placeholder="Indique el nombre de la hoja a cargar" onChange={e => setSheet(e.target.value)}/>
                                    </div>
                                ) : (
                                    <div className="formInput"></div>
                                )

                            }
                            <button className="sendButton">Enviar</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    )
}