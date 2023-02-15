import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import DriveFolderUploadIcon from '@mui/icons-material/DriveFolderUpload';
import Swal from 'sweetalert2';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

const API = process.env.REACT_APP_API;

export const New = () =>{

    const [file, setFile] = useState("");
    const [projectName, setProjectName] = useState("");
    const [fileType, setFileType] = useState("csv");
    const [sep, setSep] = useState("");
    const [enc, setEnc] = useState("UTF-8");
    const [sheet, setSheet] = useState("");
    const [open, setOpen] = useState(false);

    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);

    const handleSubmit = async (e) => {

        e.preventDefault();

        const form = new FormData();
        form.append('dataSource', file);
        form.append('pName', projectName);
        form.append('fileType', fileType);
        form.append('sep', sep);
        form.append('enc', enc);
        form.append('sheet', sheet);

        Swal.fire({
            title: 'Agregando fuente.',
            html: 'Su fuente de datos está siendo agregada, por favor espere.<br><br><b><style="color: crimson;">No cierre esta ventana hasta el que proceso haya terminado.</style></b>',
            imageUrl: 'https://www.tuyu.mx/assets/loader.gif',
            imageWidth: 100,
            imageHeight: 100,
            imageAlt: 'Custom image',
            confirmButtonColor: "#000",
            showConfirmButton: false,
            allowOutsideClick: false
          });

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
                showConfirmButton: false,
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
                <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
                    <Fade in={open}>
                        <div className="modalBox">
                            <div className="closeBtn" onClick={handleClose}>&times;</div>
                            <div className="modalContent">
                                <div className="modalTitle">
                                    <h3><b>Importar una fuente de datos</b></h3>
                                </div>
                                <div className="modalText">
                                    <p>Desde esta página de la aplicación web podrá agregar una nueva fuente de datos al DataHub. Igualmente, al agregar una nueva fuente de datos se creará un nuevo proyecto que después podrá encontrar en la página de <b>Repositorio</b>.</p>
                                    <p>A continuación, se presenta un desglose de los campos a rellenar para poder agregar una nueva fuente de datos y la descripción de estos.</p>
                                    <div className="modalTable">
                                        <table>
                                            <thead>
                                                <tr>
                                                    <th style={{width: "20%"}}>Campo</th>
                                                    <th style={{width: "80%"}}>Descripción</th>
                                                </tr>
                                            </thead>
                                            <tr>
                                                <td>Fuente de Datos</td>
                                                <td>Para cargar tu fuente de datos da click en el símbolo <DriveFolderUploadIcon className="icon" />. Después, selecciona la fuente de datos deseada y da click en <i>Abrir</i>.</td>
                                            </tr>
                                            <tr>
                                                <td>Nombre de Proyecto</td>
                                                <td>Escribe la forma en la que tu proyecto será identificado dentro del DataHub.</td>
                                            </tr>
                                            <tr>
                                                <td>Tipo de Archivo</td>
                                                <td>Selecciona qué extensión tiene el archivo de la fuente de datos que añadirás al DataHub.</td>
                                            </tr>
                                            <tr>
                                                <td>Separador</td>
                                                <td>Indica el caracter con el cual están separados los datos dentro de la fuente de datos. <b>Ejemplo: </b>En un archivo CSV el separador es la coma.</td>
                                            </tr>
                                            <tr>
                                                <td>Cotejamiento</td>
                                                <td>Indica el cotejamiento que posee la fuente de datos a añadir.</td>
                                            </tr>
                                            <tr>
                                                <td>Hoja</td>
                                                <td>Si el archivo tiene la extensión XLSX, se deberá especificar la hoja donde se encuentran los datos.</td>
                                            </tr>
                                        </table>
                                    </div>
                                    <br />
                                    <p>Al finalizar da click en el botón de <i>Importar</i> para comenzar el proceso de subida de la fuente de datos.</p>
                                </div>
                            </div>
                        </div>
                    </Fade>
                </Modal>

                <div className="top">
                    <h1 className="title">Importar Datos</h1>
                    <button onClick={handleOpen}><QuestionMarkIcon /></button>
                </div>
                <div className="bottom">
                    <div className="left">
                        <img src={file ? "https://static.thenounproject.com/png/3163111-200.png" : "https://static.thenounproject.com/png/140281-200.png"} alt="" className="placeholderImg" />
                    </div>
                    <div className="right">
                        <form>
                            <div className="formInput">
                                <label htmlFor="file">Fuente de Datos: <DriveFolderUploadIcon className="icon" /></label>
                                <input type="file" id="file" name="dataSource" onChange={e => setFile(e.target.files[0])} style={{display: "none"}} accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel, .txt"/>
                                <p>{file === '' ? 'Ningún archivo seleccionado' : file.name}</p>
                            </div>
                            <div className="formInput">
                                <label>Nombre de Proyecto</label>
                                <input type="text" name="pName" value={projectName} placeholder="Indique el nombre del proyecto" onChange={e => setProjectName(e.target.value)}/>
                            </div>
                            <div className="formInput">
                                <label>Tipo de Archivo</label>
                                <select name="fileType" onChange={e => setFileType(e.target.value)}>
                                    <option value="csv">CSV</option>
                                    <option value="xlsx">XLSX</option>
                                    <option value="txt">TXT</option>
                                </select>
                            </div>
                            <div className="formInput">
                                <label>Separador</label>
                                <input type="text" name="sep" value={sep} placeholder="Indique el separador" onChange={e => setSep(e.target.value)}/>
                            </div>
                            <div className="formInput">
                                <label>Codificación</label>
                                <select name="enc" onChange={e => setEnc(e.target.value)}>
                                    <option value="UTF-8">UTF-8</option>
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
                        </form>
                    </div>
                </div>
                <div className="send">
                    <button className="sendButton" onClick={handleSubmit}>Importar</button>
                </div>
            </div>
        </div>
    )
}