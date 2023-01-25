import React from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import { Link } from "react-router-dom";

export const FileMenu = () =>{
    return(
        <div className="perfMenu">
            <Sidebar />
            <div className="perfContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Archivos</h1>
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
                            <button className="addButton">Ver layouts</button>
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
                        <Link to={'/filemenu/rules/' + localStorage.getItem('project')}><button className="addButton">Ver Reglas</button></Link>
                        </div>
                    </div>
                    <div className="right none"></div>
                </div>
            </div>
        </div>
    )
}