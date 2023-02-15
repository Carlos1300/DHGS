import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import { Link } from "react-router-dom";
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

export const PerfMenu = () =>{

    const [open, setOpen] = useState(false);

    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);

    return(
        <div className="perfMenu">
            <Sidebar />
            <div className="perfContainer">
                <Navbar />
                <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
                    <Fade in={open}>
                        <div className="modalBox">
                        <div className="closeBtn" onClick={handleClose}>&times;</div>
                        <div className="modalContent">
                            <div className="modalTitle">
                                <h3><b>Página de Datos Perfilados</b></h3>
                            </div>
                            <div className="modalText">
                            <p>En esta página encontrarás todos los perfilados de datos que son generados por el DataHub y sus reglas, ten en cuenta que para visualizar algunos de ellos se requiere haber ejecutado alguna regla en específico en alguno de tus flujos. Para ver los perfilados que han sido creados da click en cualquiera de los botones.</p>
                            </div>
                        </div>
                        </div>
                    </Fade>
                </Modal>
                <div className="top info">
                    <h1 className="title">Datos Perfilados</h1>
                    <button onClick={handleOpen}><QuestionMarkIcon /></button>
                </div>
                <div className="top">
                    <div className="left">
                        <h1 className="title">Resumen de datos</h1>
                        <div className="item">
                            <div className="details">
                                <p>En esta sección se encuentra un resumen de las <b>medidas estadísticas (media, mediana, cuartiles, etc)</b> de la fuente de datos cargada.</p>
                            </div>
                        </div>
                        <div className="menuButton">
                            <Link to={'resume/' + localStorage.getItem('project')}><button className="addButton">Ver resumen</button></Link>
                        </div>
                    </div>
                    <div className="right">
                        <h1 className="title">Sumario de Datos</h1>
                        <div className="item">
                            <div className="details">
                                <p>En esta sección se encuentra la <b>información de las columnas (máximos, mínimos, tipo de dato, etc)</b> de la fuente de datos cargada.</p>
                                <span>Se obtiene desde la aplicación de un flujo.</span>
                            </div>
                        </div>
                        <div className="menuButton">
                            <Link to={'summary/' + localStorage.getItem('project')}><button className="addButton">Ver sumario</button></Link>
                        </div>
                    </div>
                </div>
                <div className="bottom">
                    <div className="left">
                        <h1 className="title">Frecuencia de valores</h1>
                        <div className="item">
                            <div className="details">
                                <p>En esta sección se encuentra la <b>frecuencia de un valor</b> en una columna seleccionada.</p>
                                <span>Se obtiene desde la aplicación de un flujo.</span>
                            </div>
                        </div>
                        <div className="menuButton">
                            <Link to={'frequency/' + localStorage.getItem('project')}><button className="addButton">Ver frecuencias</button></Link>
                        </div>
                    </div>
                    <div className="right">
                        <h1 className="title">Fonéticos</h1>
                        <div className="item">
                            <div className="details">
                                <p>En esta sección se encuentra la información de los <b>metáfonos y soundex</b> de una columna seleccionada.</p>
                                <span>Se obtiene desde la aplicación de un flujo.</span>
                            </div>
                        </div>
                        <div className="menuButton">
                            <Link to={'phonetics/' + localStorage.getItem('project')}><button className="addButton">Ver fonéticos</button></Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}