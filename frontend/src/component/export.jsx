import React, { useState } from 'react'
import { Sidebar } from './sidebar';
import { Navbar } from './navbar';
import { utils, writeFile } from 'xlsx';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import Swal from 'sweetalert2';

const API = process.env.REACT_APP_API;

export const Export = () => {
    const [projectName, setProjectName] = useState("");
    const [fileType, setFileType] = useState("csv");
    const [enc, setEnc] = useState("UTF-8");
    const [outputName, setOutputName] = useState("")
    const [open, setOpen] = useState(false);

    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);

    const handleSubmit = async () => {
        Swal.fire({
            title: 'Exportando datos.',
            html: 'Su fuente de datos está siendo procesada para exportarse, por favor espere.<br><br><b><style="color: crimson;">No cierre esta ventana hasta el que proceso haya terminado.</style></b>',
            imageUrl: 'https://www.tuyu.mx/assets/loader.gif',
            imageWidth: 100,
            imageHeight: 100,
            imageAlt: 'Custom image',
            showConfirmButton: false,
            allowOutsideClick: false
          });

        var project = '';

        if (localStorage.getItem('project') === 'None'){
            project = projectName;
        }else{
            project = localStorage.getItem('project')
        }

        const ExportJSON = {
            projectName: project,
            fileType: fileType,
            enc: enc,
            outputName: outputName
        }

        const res = await fetch(API + '/export_data/' + localStorage.getItem('email'),{
            method: 'POST',
            headers:{
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(ExportJSON)
        });

        const data = await res.json();

        if(res.status !== 200){
            Swal.fire({
                title: 'Error al exportar la fuente de datos',
                text: 'Contacte a soporte técnico.',
                icon: 'error',
                showConfirmButton: false,
                timer: "10000"
            });
        }else{
            if (data.type === 'xlsx'){
                let ws = utils.json_to_sheet(data.data);
                let wb = utils.book_new();
                utils.book_append_sheet(wb, ws, "Hoja1");
                writeFile(wb, data.filename);

                Swal.fire({
                    title: 'Exportación exitosa',
                    text: 'Se han exportado los datos en un archivo XLSX.',
                    icon: 'success',
                    showConfirmButton: false,
                    timer: "10000"
                });
    
                setProjectName('');
    
            } else if(data.type === 'csv'){
                const url = window.URL.createObjectURL(new Blob(["\ufeff", data.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', data.filename);
                document.body.appendChild(link);
                link.click();

                Swal.fire({
                    title: 'Exportación exitosa',
                    text: 'Se han exportado los datos en un archivo CSV.',
                    icon: 'success',
                    showConfirmButton: false,
                    timer: "10000"
                });
    
                setProjectName('');
            }else{
                const url = URL.createObjectURL(new Blob(["\ufeff", data.data], { type: "text/plain" }));
                const link = document.createElement("a");
                link.download = data.filename;
                link.href = url;
                link.click();

                Swal.fire({
                    title: 'Exportación exitosa',
                    text: 'Se han exportado los datos en un archivo TXT.',
                    icon: 'success',
                    showConfirmButton: false,
                    timer: "10000"
                });
    
                setProjectName('');
            }
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
                                    <h3><b>Exportar datos procesados</b></h3>
                                </div>
                                <div className="modalText">
                                    <p>Desde esta página de la aplicación web podrá exportar los datos procesados que son generados después de haber aplicado un flujo. Estos datos procesados se descargarán a su computadora para que pueda comprobarlos y manipularlos como guste.</p>
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
                                                <td>Nombre del Archivo</td>
                                                <td>Escribe el nombre que llevará el archivo que contendrá los datos procesados por el DataHub.</td>
                                            </tr>
                                            <tr>
                                                <td>Tipo de Archivo</td>
                                                <td>Selecciona qué extensión tendrá el archivo que descargarás a tu computadora.</td>
                                            </tr>
                                            <tr>
                                                <td>Cotejamiento</td>
                                                <td>Indica el cotejamiento que tendrá el archivo de datos procesados.</td>
                                            </tr>
                                        </table>
                                    </div>
                                    <br />
                                    <p>Al finalizar da click en el botón de <i>Exportar</i> para comenzar el proceso de descarga de los datos procesados.</p>
                                </div>
                            </div>
                        </div>
                    </Fade>
                </Modal>

                <div className="top">
                    <h1 className="title">Exportar Datos</h1>
                    <button onClick={handleOpen}><QuestionMarkIcon /></button>
                </div>
                <div className="bottom export">
                    <form>
                        {
                            localStorage.getItem('project') !== 'None' ? (
                            <></>        
                            ) : (

                                <div className="formInput">
                                    <label>Nombre del Proyecto</label>
                                    <input type="text" name="pName" value={projectName} placeholder="Nombre de proyecto" onChange={e => setProjectName(e.target.value)}/>
                                </div>
                            )
                        }
                        <div className="formInput">
                            <label>Nombre del Archivo</label>
                            <input type="text" name='oName' value={outputName} placeholder="Nombre del archivo" onChange={e => setOutputName(e.target.value)}/>
                        </div>
                        <div className="formInput">
                            <label>Tipo de Archivo</label>
                            <select name="fileType" onChange={e => setFileType(e.target.value)}>
                                <option value="csv" selected>CSV</option>
                                <option value="xlsx">XLSX</option>
                                <option value="txt">TXT</option>
                                {/* <option value="json">JSON</option> */}
                            </select>
                        </div>
                        <div className="formInput">
                            <label>Cotejamiento</label>
                            <select name="enc" onChange={e => setEnc(e.target.value)}>
                                <option value="UTF-8" selected>UTF-8</option>
                                <option value="ISO-8859-1">ISO-8859-1</option>
                                <option value="LATIN-1">LATIN-1</option>
                                <option value="OTRO">OTRO</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div className='exportButton'>
                    <button className="sendButton" onClick={handleSubmit}>Exportar</button>
                </div>
            </div>
        </div>
    )
}
