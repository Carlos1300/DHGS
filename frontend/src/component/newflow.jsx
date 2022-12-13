import React, { useState } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
// import swal from 'sweetalert';

const API = process.env.REACT_APP_API;

export const NewFlow = () =>{

    const [rulesList, setRulesList] = useState([{ rule : '' }]);

    // const handleSubmit = async (e) => {

    //     e.preventDefault();

    //     const form = new FormData();
    //     form.append('dataSource', file);
    //     form.append('pName', projectName);
    //     form.append('fileType', fileType);
    //     form.append('sep', sep);
    //     form.append('enc', enc);

    //     console.log(URL.createObjectURL(file))

    //     const res = await fetch(API + '/addProject/' + localStorage.getItem('email'),{
    //         method: 'POST',
    //         headers:{
    //             "Access-Control-Allow-Origin": "*"
    //         },
    //         body: form
    //     });

    //     const data = await res.json();

    //     if(res.status !== 200 && data.msg !== ''){
    //         swal({
    //             title: 'Error al cargar la fuente de datos',
    //             text: 'Revise de nuevo los campos.',
    //             icon: 'error',
    //             button: 'Volver a intentarlo',
    //             confirmButtonColor: "#000",
    //             timer: "10000"
    //         });

    //         setFile('');
    //         setProjectName('');
    //         setFileType('');
    //         setSep('');
    //         setEnc('');

    //     }else{
    //         swal({
    //             title: 'Carga exitosa',
    //             text: data.msg + ' : ' + data.objID,
    //             icon: 'success',
    //             button: 'Continuar',
    //             confirmButtonColor: "#000",
    //             timer: "10000"
    //         })

    //         setFile('');
    //         setProjectName('');
    //         setFileType('');
    //         setSep('');
    //         setEnc('');
    //     }
        
    // }

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <div className="top">
                    <h1 className="title">Agregar Flujo</h1>
                </div>
                <div className="bottom">
                    <div className="right">
                        <form>
                            <div className="formInput">
                                <label>Flujo</label>
                                <input type="text" name="flow" placeholder="Indique el nombre del flujo"/>
                            </div>
                            <div className="formInput">
                                <label>Descripción</label>
                                <p>Descripción de lo que hace el flujo.</p>
                            </div>
                            <div className="formInput">
                                <button className="sendButton">Añadir regla</button>
                            </div>
                            <button className="sendButton">Send</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    )
}