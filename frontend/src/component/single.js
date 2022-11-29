import React from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import { Chart } from "./chart";
import { TableUI } from "./table";

export const Single = () => {

    return(
        <div className="single">
            <Sidebar />
            <div className="singleContainer">
                <Navbar />
                <div className="top">
                    <div className="left">
                        <div className="editButton">Editar</div>
                        <h1 className="title">Mi Cuenta</h1>
                        <div className="item">
                            <div className="details">
                                <h1 className="itemTitle">{localStorage.getItem('name')}</h1>
                                <div className="detailItem">
                                    <span className="itemKey">Email:</span>
                                    <span className="itemValue">{localStorage.getItem('email')}</span>
                                </div>
                                <div className="detailItem">
                                    <span className="itemKey">Teléfono:</span>
                                    <span className="itemValue">{localStorage.getItem('tel')}</span>
                                </div>
                                <div className="detailItem">
                                    <span className="itemKey">Calle:</span>
                                    <span className="itemValue">{localStorage.getItem('address')}</span>
                                </div>
                                <div className="detailItem">
                                    <span className="itemKey">País:</span>
                                    <span className="itemValue">{localStorage.getItem('country')}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="right">
                        <Chart aspect={3 / 1} title= "User Activity (last 6 months)" />
                    </div>
                </div>
                <div className="bottom">
                <h1 className="title">Últimas Acciones</h1>
                    <TableUI />
                </div>
            </div>
        </div>
    )
}