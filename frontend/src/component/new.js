import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import DriveFolderUploadIcon from '@mui/icons-material/DriveFolderUpload';

export const New = () =>{

    const [file, setFile] = useState("");

    console.log(file)

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Nuevo</h1>
                </div>
                <div className="bottom">
                    <div className="left">
                        <img src={file ? URL.createObjectURL(file) : "https://segudirecto.com.mx/wp-content/themes/consultix/images/no-image-found-360x260.png"} alt="" className="placeholderImg" />
                    </div>
                    <div className="right">
                        <form>
                            <div className="formInput">
                                <label htmlFor="file">Image: <DriveFolderUploadIcon className="icon" /></label>
                                <input type="file" id="file" onChange={e=>setFile(e.target.files[0])} style={{display: "none"}} accept="image/*"/>
                            </div>
                            <div className="formInput">
                                <label>Usuario</label>
                                <input type="text" placeholder="nuevo_usuario" />
                            </div>
                            <div className="formInput">
                                <label>Nombre Completo</label>
                                <input type="text" placeholder="Nuevo Usuario" />
                            </div>
                            <div className="formInput">
                                <label>Email</label>
                                <input type="email" placeholder="nusuario@gmail.com" />
                            </div>
                            <div className="formInput">
                                <label>Teléfono</label>
                                <input type="text" placeholder="23132164513" />
                            </div>
                            <div className="formInput">
                                <label>Contraseña</label>
                                <input type="contraseña" />
                            </div>
                            <div className="formInput">
                                <label>Calle</label>
                                <input type="text" placeholder="Calle de Ejemplo" />
                            </div>
                            <div className="formInput">
                                <label>País</label>
                                <input type="text" placeholder="México" />
                            </div>
                            <button className="sendButton">Send</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    )
}