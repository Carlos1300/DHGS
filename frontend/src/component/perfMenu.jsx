import React from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import { Link } from "react-router-dom";

export const PerfMenu = () =>{
    return(
        <div className="perfMenu">
            <Sidebar />
            <div className="perfContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Datos Perfilados</h1>
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
                            <button className="addButton">Ver frecuencias</button>
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
                            <button className="addButton">Ver fonéticos</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}