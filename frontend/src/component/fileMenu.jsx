import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import { Link } from "react-router-dom";
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

export const FileMenu = () =>{

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
                                <h3><b>Página de Archivos</b></h3>
                            </div>
                            <div className="modalText">
                            <p>En esta página encontrarás los archivos que hayas cargado al DataHub, ten en cuenta que para visualizar algunos de ellos se requiere tener un proyecto activo. Para ver los archivos que has agregado al DataHub da click en cualquiera de los botones.</p>
                            </div>
                        </div>
                        </div>
                    </Fade>
                </Modal>
                <div className="top info">
                    <h1 className="title">Archivos</h1>
                    <button onClick={handleOpen}><QuestionMarkIcon /></button>
                </div>
                <div className="top">
                    <div className="left">
                        <h1 className="title">Catálogos</h1>
                        <div className="item">
                            <div className="details">
                                <p>En esta sección se encuentran todos los catálogos disponibles que ofrece el DataHub y los subidos por los usuarios.</p>
                            </div>
                        </div>
                        <div className="menuButton">
                            <Link to='/filemenu/catalogs'><button className="addButton">Ver catálogos</button></Link>
                        </div>
                    </div>
                    <div className={localStorage.getItem('project') === 'None' ? 'right none' : 'right'}>
                        <h1 className="title">Layouts</h1>
                        <div className="item">
                            <div className="details">
                                <p>En esta sección se encuentran aquellos layouts que han sido cargados por el usuario.</p>
                            </div>
                        </div>
                        <div className="menuButton">
                            <Link to={'layouts/' + localStorage.getItem('project')}><button className="addButton">Ver layouts</button></Link>
                        </div>
                    </div>
                </div>

                <div className="bottom">
                    <div className={localStorage.getItem('project') === 'None' ? 'right none' : 'right'}>
                        <h1 className="title">Reglas</h1>
                        <div className="item">
                            <div className="details">
                                <p>En esta sección se encontrarán los detalles de las reglas definidas por el usuario.</p>
                            </div>
                        </div>
                        <div className="menuButton">
                        <Link to={'rules/' + localStorage.getItem('project')}><button className="addButton">Ver reglas</button></Link>
                        </div>
                    </div>
                    <div className="right none"></div>
                </div>
            </div>
        </div>
    )
}